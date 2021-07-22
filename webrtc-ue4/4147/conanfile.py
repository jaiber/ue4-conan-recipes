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
    
    def cmake_flags(self):
        
        from ue4util import Utility
        
        openssl = self.deps_cpp_info["OpenSSL"]

            #"-DGN_EXTRA_ARGS=is_debug=false is_component_build=false is_clang=false rtc_enable_protobuf=false rtc_build_ssl=false rtc_include_tests=false rtc_use_h264=true use_rtti=true use_custom_libcxx=true treat_warnings_as_errors=false use_ozone=true rtc_ssl_root='" + openssl.rootpath + "'",
            #"-DGN_EXTRA_ARGS=\"is_debug=false is_component_build=false rtc_enable_protobuf=false rtc_include_tests=false\"",
        return [
            "-DGN_EXTRA_ARGS=\"is_debug=false is_component_build=false rtc_enable_protobuf=false rtc_include_tests=false rtc_use_h264=true use_rtti=true treat_warnings_as_errors=false use_ozone=true\"",
            "-DWEBRTC_BRANCH_HEAD=refs/remotes/branch-heads/4147"
        ]
    
    def source(self):
        
        tools.untargz("/home/i2a/jj/unreal/tmp/t/libwebrtc-build13.tar.gz", destination=".", pattern=None, strip_root=False)
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
        self.cpp_info.includedirs = [os.path.join("include", "webrtc")]
        
        # Provide the necessary data so that consumers can instantiate a `ProtoCompiler` object
        self.env_info.PYTHONPATH.append(self.package_folder)
