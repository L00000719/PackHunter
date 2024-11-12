# PackHunter: Recovering Missing Packages for C/C++ Projects

## Dataset
We choose the projects with missing package errors that are investigated in our empirical study.

### Empircal_Study

This page lists 47 projects that failed to build in our empirical study, including categories of errors such as missing package error (30 out of 47), build script error (7 out of 47), source code error (5 out of 47), and miscellaneous error (5 out of 47). For the projects that failed to build due to missing package errors, we have listed the specific packages that were missing.

| Project | Url | Root Causes | Missing Packages |
|---------|-----|-------------|-----------------|
| antirez/dump1090 | https://github.com/antirez/dump1090 | missing package | librtlsdr-dev |
| google/guetzli | https://github.com/google/guetzli | missing package | libpng-dev | 
| abrasive/shairport | https://github.com/abrasive/shairport | missing package | libpulse-dev libavahi-client-dev libssl-dev libasound2-dev libao-dev |
| coturn/coturn | https://github.com/coturn/coturn | missing package | libssl-dev libevent-dev libpq-dev libhiredis-dev libsystemd-dev libsqlite3-dev libmysqlclient-dev libmongoc-dev |
| clibs/clib | https://github.com/clibs/clib | missing package | libcurl4-gnutls-dev |
| jonas/tig | https://github.com/jonas/tig | missing package | libncurses-dev |
| eclipse/paho.mqtt.c | https://github.com/eclipse/paho.mqtt.c | missing package | libssl-dev |
| glfw/glfw | https://github.com/glfw/glfw | missing package | libxrandr-dev libxi-dev libxcursor-dev libxinerama-dev |
| fireice-uk/xmr-stak | https://github.com/fireice-uk/xmr-stak | missing package | libmicrohttpd-dev libssl-dev libhwloc-dev |
| tmux/tmux | https://github.com/tmux/tmux | missing package | libevent-dev libncurses-dev | 
| erincatto/box2d | https://github.com/erincatto/box2d | missing package | libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev |
| sogou/workflow | https://github.com/sogou/workflow | missing package | libssl-dev |
| Gargaj/Bonzomatic | https://github.com/Gargaj/Bonzomatic | missing package | libglu1-mesa-dev libasound2-dev libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev |
| raysan5/raylib | https://github.com/raysan5/raylib | missing package | libxrandr-dev libxi-dev libgl-dev libxcursor-dev libxinerama-dev |
| TheAlgorithms/C | https://github.com/TheAlgorithms/C | missing package | libopengl-dev freeglut3-dev |
| SFML/SFML | https://github.com/SFML/SFML | missing package | libx11-dev libxrandr-dev libxcursor-dev libgl1-mesa-dev libudev-dev libfreetype6-dev libopenal-dev libflac-dev libvorbis-dev |
| RainerKuemmerle/g2o | https://github.com/RainerKuemmerle/g2o | missing package | libeigen3-dev | 
| JoeyDeVries/LearnOpenGL | https://github.com/JoeyDeVries/LearnOpenGL | missing package | libassimp-dev libxrandr-dev libglfw3-dev libxinerama-dev libxcursor-dev libxi-dev libfreetype-dev libxxf86vm-dev |
| xmrig/xmrig | https://github.com/xmrig/xmrig | missing package | libuv1-dev libssl-dev libhwloc-dev |
| ZLMediaKit/ZLMediaKit | https://github.com/ZLMediaKit/ZLMediaKit | missing package | libssl-dev |
| minetest/minetest | https://github.com/minetest/minetest | missing package | libpng-dev libjpeg-dev libxi-dev libgl1-mesa-dev libsqlite3-dev libogg-dev libvorbis-dev libopenal-dev libcurl4-gnutls-dev libfreetype6-dev zlib1g-dev libgmp-dev libjsoncpp-dev libzstd-dev libluajit-5.1-dev libsdl2-dev |
| libgit2/libgit2 | https://github.com/libgit2/libgit2 | missing package | libssl-dev |
| OpenRCT2/OpenRCT2 | https://github.com/OpenRCT2/OpenRCT2 | missing package | libsdl2-dev libfreetype6-dev libfontconfig1-dev libzip-dev libpng-dev libspeexdsp-dev libcurl4-openssl-dev nlohmann-json3-dev libssl-dev libicu-dev zlib1g-dev libgl1-mesa-dev |
| Project-OSRM/osrm-backend | https://github.com/Project-OSRM/osrm-backend | missing package | libbz2-dev libzip-dev libboost-all-dev liblua5.2-dev libtbb-dev |
| postgres/postgres | https://github.com/postgres/postgres | missing package | libicu-dev libreadline-dev |
| supertuxkart/stk-code | https://github.com/supertuxkart/stk-code | missing package | libbluetooth-dev libsdl2-dev libcurl4-openssl-dev libfreetype6-dev libharfbuzz-dev libjpeg-dev libopenal-dev libpng-dev libssl-dev libvorbis-dev libmbedtls-dev zlib1g-dev |
| PointCloudLibrary/pcl | https://github.com/PointCloudLibrary/pcl | missing package | libeigen3-dev libboost-all-dev libflann-dev |
| pocoproject/poco | https://github.com/pocoproject/poco | missing package | libssl-dev |
| VowpalWabbit/vowpal_wabbit | https://github.com/VowpalWabbit/vowpal_wabbit | missing package | libfmt-dev libspdlog-dev libboost-all-dev |
| mamedev/mame | https://github.com/mamedev/mame | missing package | libjpeg9-dev qtbase5-dev librm-dev libportmidi-dev libfreetype-dev libgig-dev libnglib-dev libceres-dev libfontconfig-dev portaudio19-dev libutf8proc-dev libsharp-dev libasmjit-dev libsdl2-ttf-dev libzstd-dev |
| EZLippi/Tinyhttpd | https://github.com/EZLippi/Tinyhttpd | Build script |
| cesanta/mongoose | https://github.com/cesanta/mongoose | Build script |
| yrutschle/sslh | https://github.com/yrutschle/sslh | Build script |
| MrGlockenspiel/activate-linux | https://github.com/MrGlockenspiel/activate-linux | Build script |
| NVIDIA/cuda-samples | https://github.com/NVIDIA/cuda-samples | Build script |
| pgbouncer/pgbouncer | https://github.com/pgbouncer/pgbouncer | Build script |
| albfan/miraclecast | https://github.com/albfan/miraclecast | Build script |
| beanstalkd/beanstalkd | https://github.com/beanstalkd/beanstalkd | source code |
| bartobri/no-more-secrets | https://github.com/bartobri/no-more-secrets | source code |
| mozilla/mozjpeg | https://github.com/mozilla/mozjpeg | source code |
| AFLplusplus/AFLplusplus | https://github.com/AFLplusplus/AFLplusplus | source code |
| haproxy/haproxy | https://github.com/haproxy/haproxy | source code |
| orangeduck/Corange | https://github.com/orangeduck/Corange | other |
| TelegramMessenger/MTProxy | https://github.com/TelegramMessenger/MTProxy | other |
| sustrik/libmill | https://github.com/sustrik/libmill | other |
| minoca/os | https://github.com/minoca/os | other |
| vmg/sundown | https://github.com/vmg | other |

## PackHunter
PackHunter is a tool that automates the recovery of missing packages in C/C++ projects.

### Dependencies
PackHunter analyze the source code by using [*srcML*](https://www.srcml.org/)

### Usage
run command:
```
cd packhunter
python3 packhunter.py --path=$project_directory
```

### Test
```tests``` directory contains several projects used to test PackHunter.
