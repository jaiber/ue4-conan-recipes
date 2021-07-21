from conans import ConanFile, CMake, tools
import json, os

class FakeX11Conan(ConanFile):
    name = "fakex11-ue4"
    version = "1.0"
    license = "Apache-2.0"
    url = "https://github.com/adamrehn/ue4-conan-recipes/fakex11-ue4"
    description = "fakex11 custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    short_paths = True
    exports = "*.py"
    requires = (
        "libcxx/ue4@adamrehn/profile",
        "ue4util/ue4@adamrehn/profile"
    )
    
    def requirements(self):
        self.requires("zlib/ue4@adamrehn/{}".format(self.channel))
    
    def cmake_flags(self):
        return []
    
    def source(self):
        
        self.run(" ".join([
            "git", "clone",
            "--progress",
            "https://github.com/jaiber/fakex11.git"
        ]))

    def build(self):
        
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Build grpc
        cmake = CMake(self)
        cmake.configure(source_folder="fakex11", args=self.cmake_flags())
        cmake.build()
        cmake.install()
    
    def package(self):
        self.copy("__init__.py")
        self.copy(pattern="*.a", src="lib", dst="lib")
    
    def package_info(self):
        
        # Filter out any extensions when listing our exported libraries
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs = list([lib for lib in self.cpp_info.libs if "_ext" not in lib])
