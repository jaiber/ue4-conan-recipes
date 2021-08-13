from conans import ConanFile, CMake, tools
import json, os

class MediaSoupBroadCasterDemo(ConanFile):
    name = "mediasoup-broadcaster-demo-ue4"
    version = "1.0"
    license = "Apache-2.0"
    url = "https://github.com/adamrehn/ue4-conan-recipes/mediasoup-broadcaster-demo-ue4"
    description = "Mediasoup Broadcaster Demo - custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    short_paths = True
    exports = "*.py"
    requires = (
        "libcxx/ue4@adamrehn/profile",
        "ue4util/ue4@adamrehn/profile"
    )
    
    def requirements(self):
        pass
        self.requires("OpenSSL/ue4@adamrehn/{}".format(self.channel))
        self.requires("zlib/ue4@adamrehn/{}".format(self.channel))
        self.requires("toolchain-wrapper/ue4@adamrehn/{}".format(self.channel))
        #self.requires("webrtc-ue4/4147@{}/{}".format(self.user, self.channel))
    
    def cmake_flags(self):
        
        # Retrieve the absolute paths to libprotobuf, libprotoc, and protoc
        from ue4util import Utility
        
        # Generate the CMake flags to use our custom dependencies
        #zlib = self.deps_cpp_info["zlib"]
        #    "-DZLIB_LIBRARY=" + Utility.resolve_file(zlib.lib_paths[0], zlib.libs[0]),
        #webrtc = self.deps_cpp_info["webrtc-ue4"]
        #    "-DLIBWEBRTC_INCLUDE_PATH=/home/i2a/.conan/data/webrtc-ue4/4147/adamrehn/4.26/package/cf215c4a8185de8d12f55fd36319783163268e03/include/webrtc/", #" + webrtc.include_paths[0],
        openssl = self.deps_cpp_info["OpenSSL"]
        toolchain = self.deps_cpp_info["toolchain-wrapper"]
        return [
            "-DLIBWEBRTC_INCLUDE_PATH=/home/i2a/.conan/data/webrtc-ue4/4147/adamrehn/4.26/build/cf215c4a8185de8d12f55fd36319783163268e03/webrtc/src",
            "-DLIBWEBRTC_BINARY_PATH=/home/i2a/.conan/data/webrtc-ue4/4147/adamrehn/4.26/package/cf215c4a8185de8d12f55fd36319783163268e03/lib", # + webrtc.lib_paths[0],
            "-DOPENSSL_INCLUDE_DIR:PATH=" + openssl.include_paths[0],
            "-DCMAKE_USE_OPENSSL=ON",
            "-DCMAKE_CXX_FLAGS=-stdlib=libc++ -nostdinc++ -I" + toolchain.include_paths[0] + "../libc++/include/c++/v1 -L" + toolchain.lib_paths[0]
        ]
    
    def source(self):
        
        self.run(" ".join([
            "git", "clone",
            "--progress",
            "https://github.com/jaiber/mediasoup-broadcaster-demo.git"
        ]))

    def build(self):
        
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Build grpc
        cmake = CMake(self)
        cmake.verbose = True
        cmake.configure(source_folder="mediasoup-broadcaster-demo", args=self.cmake_flags())
        cmake.build()
        cmake.install()
    
    def package(self):
        self.copy("__init__.py")
        self.copy(pattern="*.a", src="libwebrtc", dst="lib")
        self.copy(pattern="*.hpp", src="_deps/mediasoupclient-src/include", dst="include/mediasoupclient")
    
    def package_info(self):
        
        # Filter out any extensions when listing our exported libraries
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs = list([lib for lib in self.cpp_info.libs if "_ext" not in lib])
        self.cpp_info.includedirs = [os.path.join("include", "mediasoupclient"), os.path.join("include", "sdptransform")]
        
        self.env_info.PYTHONPATH.append(self.package_folder)
