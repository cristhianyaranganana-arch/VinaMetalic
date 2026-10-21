cmake_minimum_required(VERSION 3.12)

project(VinaMetalic VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# Audit finding #12: build portable binaries by default. Static Boost removes
# the runtime dependency that made source builds non-portable. Turn this OFF
# for system-integration builds (e.g. macOS/homebrew ships shared-only).
option(USE_STATIC_BOOST "Statically link the Boost libraries (portable binaries)" ON)
set(Boost_USE_STATIC_LIBS ${USE_STATIC_BOOST})

find_package(Boost 1.65 REQUIRED COMPONENTS
    system
    thread
    serialization
    filesystem
    program_options
)
find_package(Threads REQUIRED)

set(VINAMETALIC_LIB_SOURCES
    src/lib/ad4cache.cpp
    src/lib/cache.cpp
    src/lib/conf_independent.cpp
    src/lib/coords.cpp
    src/lib/grid.cpp
    src/lib/metal_parameters.cpp
    src/lib/metal_scoring.cpp
    src/lib/model.cpp
    src/lib/monte_carlo.cpp
    src/lib/mutate.cpp
    src/lib/non_cache.cpp
    src/lib/parallel_mc.cpp
    src/lib/parse_pdbqt.cpp
    src/lib/quasi_newton.cpp
    src/lib/quaternion.cpp
    src/lib/random.cpp
    src/lib/szv_grid.cpp
    src/lib/utils.cpp
    src/lib/vina.cpp
)

add_library(vinametalic_core STATIC ${VINAMETALIC_LIB_SOURCES})
target_include_directories(vinametalic_core PUBLIC src/lib ${Boost_INCLUDE_DIRS})
target_link_libraries(vinametalic_core PUBLIC ${Boost_LIBRARIES} Threads::Threads)

add_executable(vina src/main/main.cpp)
target_link_libraries(vina PRIVATE vinametalic_core)
target_compile_definitions(vina PRIVATE VERSION="v1.0.0")

add_executable(vina_split src/split/split.cpp)
target_link_libraries(vina_split PRIVATE vinametalic_core)
target_compile_definitions(vina_split PRIVATE VERSION="v1.0.0")

install(TARGETS vina vina_split RUNTIME DESTINATION bin)

include(CTest)
if(BUILD_TESTING)
    add_executable(metal_gradient_test tests/metal_gradient_test.cpp)
    target_link_libraries(metal_gradient_test PRIVATE vinametalic_core)
    add_test(NAME metal_gradient COMMAND metal_gradient_test)

    find_package(Python3 COMPONENTS Interpreter)
    if(Python3_FOUND)
        add_test(NAME cn_detection
            COMMAND Python3::Interpreter
                ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_cn_detection.py
                $<TARGET_FILE:vina>
                ${CMAKE_CURRENT_SOURCE_DIR}
        )
    endif()

    # Audit findings #13/#14: automate the byte-identical regression suite
    # against an upstream AutoDock Vina 1.2.7 binary. OFF by default; enable
    # with -DVINA_REGRESSION_TEST=ON -DVINA_127_BIN=/path/to/vina_1.2.7.
    option(VINA_REGRESSION_TEST "Byte-identical regression tests vs AutoDock Vina 1.2.7" OFF)
    set(VINA_127_BIN "" CACHE FILEPATH "Path to an AutoDock Vina 1.2.7 reference binary")
    if(VINA_REGRESSION_TEST)
        if(NOT VINA_127_BIN OR NOT EXISTS "${VINA_127_BIN}")
            message(FATAL_ERROR "VINA_REGRESSION_TEST=ON requires -DVINA_127_BIN=<path to a Vina 1.2.7 binary>")
        endif()
        find_program(BASH_EXECUTABLE bash REQUIRED)
        foreach(REG_TEST no_metal na_receptor)
            add_test(NAME regression_${REG_TEST}
                COMMAND ${BASH_EXECUTABLE}
                    ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_regression_${REG_TEST}.sh
                    $<TARGET_FILE:vina>
                    ${VINA_127_BIN}
            )
        endforeach()
    endif()
endif()
