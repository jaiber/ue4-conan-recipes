from conans import ConanFile, CMake, tools
import json, os

class MediaSoupClientConan(ConanFile):
    name = "mediasoupclient-ue4"
    version = "3.1.5"
    license = "Apache-2.0"
    url = "https://github.com/adamrehn/ue4-conan-recipes/mediasoupclient-ue4"
    description = "MediasoupClient custom build for Unreal Engine 4"
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
        self.requires("webrtc-ue4/4147@{}/{}".format(self.user, self.channel))
    
    def cmake_flags(self):
        
        # Retrieve the absolute paths to libprotobuf, libprotoc, and protoc
        from ue4util import Utility
        
        # Generate the CMake flags to use our custom dependencies
        zlib = self.deps_cpp_info["zlib"]
        webrtc = self.deps_cpp_info["webrtc-ue4"]
        return [
            "-DLIBWEBRTC_INCLUDE_PATH=" + webrtc.include_paths[0] + "/webrtc",
            "-DLIBWEBRTC_BINARY_PATH=" + webrtc.lib_paths[0],
            "-DZLIB_LIBRARY=" + Utility.resolve_file(zlib.lib_paths[0], zlib.libs[0]),
        ]
    
    def source(self):
        
        self.run(" ".join([
            "git", "clone",
            "--progress",
            "https://github.com/versatica/libmediasoupclient.git"
        ]))

    def build(self):
        
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Build grpc
        cmake = CMake(self)
        cmake.configure(source_folder="libmediasoupclient", args=self.cmake_flags())
        cmake.build()
        cmake.install()
    
    def package(self):
        self.copy("__init__.py")
    
    def package_info(self):
        
        # Filter out any extensions when listing our exported libraries
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs = list([lib for lib in self.cpp_info.libs if "_ext" not in lib])
        
        self.env_info.PYTHONPATH.append(self.package_folder)
