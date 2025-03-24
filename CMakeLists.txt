cmake_minimum_required(VERSION 3.18.0)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

project(
    ${SKBUILD_PROJECT_NAME}
    VERSION ${SKBUILD_PROJECT_VERSION}
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_subdirectory(CDT/CDT CDT)
add_subdirectory(pybind11)
pybind11_add_module(${SKBUILD_PROJECT_NAME} cdt_bindings.cpp)
target_link_libraries(${SKBUILD_PROJECT_NAME} PRIVATE CDT::CDT)
install(TARGETS ${SKBUILD_PROJECT_NAME} LIBRARY DESTINATION .)
