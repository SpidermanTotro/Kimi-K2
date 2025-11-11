cmake_minimum_required(VERSION 3.10)
project(TheForge VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# THE FORGE C++ Components
add_executable(forge_core
    src/core/main.cpp
)

# Video processing module
add_library(forge_video SHARED
    src/video/processor.cpp
)

# Install targets
install(TARGETS forge_core DESTINATION bin)
install(TARGETS forge_video DESTINATION lib)

message(STATUS "THE FORGE - C++ Build Configuration Complete")
