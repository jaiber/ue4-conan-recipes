from conans import ConanFile, CMake, tools
import json, os

class WebRTCUe4Conan(ConanFile):
    name = "webrtc-ue4"
    version = "4147"
    license = "Apache-2.0"
    url = "https://github.com/adamrehn/ue4-conan-recipes/webrtc-ue4"
    description = "webRTC custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    short_paths = True
    exports = "*.py"
    requires = (
        "libcxx/ue4@adamrehn/profile",
        "ue4util/ue4@adamrehn/profile"
    )
    
    def requirements(self):
        self.requires("OpenSSL/ue4@adamrehn/{}".format(self.channel))
        self.requires("zlib/ue4@adamrehn/{}".format(self.channel))
        self.requires("cares-ue4/1.16.1@{}/{}".format(self.user, self.channel))
        #self.requires("protobuf-ue4/3.17.3@{}/{}".format(self.user, self.channel))
    
    def cmake_flags(self):
        
        from ue4util import Utility
        
        # Generate the CMake flags to use our custom dependencies
        openssl = self.deps_cpp_info["OpenSSL"]
        zlib = self.deps_cpp_info["zlib"]
        return [
            "-DGN_EXTRA_ARGS=is_debug=false is_component_build=false is_clang=false rtc_include_tests=false rtc_use_h264=true use_rtti=true use_custom_libcxx=false treat_warnings_as_errors=false use_ozone=true",
            "-DWEBRTC_BRANCH_HEAD=refs/remotes/branch-heads/4147",
            "-DgRPC_SSL_PROVIDER=package",
            "-DgRPC_ZLIB_PROVIDER=package",
            "-DOPENSSL_SYSTEM_LIBRARIES={}".format(";".join(openssl.system_libs)),
            "-DOPENSSL_USE_STATIC_LIBS=ON",
            "-DOPENSSL_ROOT_DIR=" + openssl.rootpath,
            "-DZLIB_INCLUDE_DIR=" + zlib.include_paths[0],
            "-DZLIB_LIBRARY=" + Utility.resolve_file(zlib.lib_paths[0], zlib.libs[0]),
        ]
    
    def source(self):
        
        tools.untargz("/home/i2a/jj/unreal/tmp/t/libwebrtc-build.tar.gz", destination=".", pattern=None, strip_root=False)
        #self.run(" ".join([
        #    "git", "clone",
        #    "--progress",
        #    "https://github.com/jaiber/libwebrtc-build"
        #]))

    def build(self):
        
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Build grpc
        cmake = CMake(self)
        cmake.configure(source_folder="libwebrtc-build", args=self.cmake_flags())
        cmake.build()
        cmake.install()
    
    def package(self):
        self.copy("__init__.py")
        self.copy(pattern="*.h", src="webrtc/src/third_party/abseil-cpp/absl", dst="include/webrtc/absl")
        self.copy(pattern="*.a", src="lib", dst="lib")
    
    def package_info(self):
        
        # Filter out any extensions when listing our exported libraries
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs = list([lib for lib in self.cpp_info.libs if "_ext" not in lib])
        
        # Provide the necessary data so that consumers can instantiate a `ProtoCompiler` object
        self.env_info.PYTHONPATH.append(self.package_folder)
