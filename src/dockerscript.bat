@echo off
set par1=%1
set par2=%2

IF "%par1%"=="build" (
    
    docker container remove -f charge_station_10
    docker container remove -f charge_station_09
    docker container remove -f charge_station_08
    docker container remove -f charge_station_07
    docker container remove -f charge_station_06
    docker container remove -f charge_station_05
    docker container remove -f charge_station_04
    docker container remove -f charge_station_03
    docker container remove -f charge_station_02
    docker container remove -f charge_station_01
    docker container remove -f charge_server_04
    docker container remove -f charge_server_03
    docker container remove -f charge_server_02
    docker container remove -f charge_server_01
    docker network remove dev_bridge
    docker image remove python-redes-image

    docker build -t python-redes-image .
    docker network create dev_bridge
)

IF "%par1%"=="saveimage" (

    docker save python-redes-image:latest -o python-redes-image.tar
)

IF "%par1%"=="loadimage" (

    docker container remove -f charge_station_10
    docker container remove -f charge_station_09
    docker container remove -f charge_station_08
    docker container remove -f charge_station_07
    docker container remove -f charge_station_06
    docker container remove -f charge_station_05
    docker container remove -f charge_station_04
    docker container remove -f charge_station_03
    docker container remove -f charge_station_02
    docker container remove -f charge_station_01
    docker container remove -f charge_server_04
    docker container remove -f charge_server_03
    docker container remove -f charge_server_02
    docker container remove -f charge_server_01
    docker network remove dev_bridge
    docker image remove python-redes-image

    docker load -i python-redes-image.tar
    docker network create dev_bridge
)

IF "%par1%"=="run" (

    docker container remove -f charge_station_10
    docker container remove -f charge_station_09
    docker container remove -f charge_station_08
    docker container remove -f charge_station_07
    docker container remove -f charge_station_06
    docker container remove -f charge_station_05
    docker container remove -f charge_station_04
    docker container remove -f charge_station_03
    docker container remove -f charge_station_02
    docker container remove -f charge_station_01
    docker container remove -f charge_server_04
    docker container remove -f charge_server_03
    docker container remove -f charge_server_02
    docker container remove -f charge_server_01

    docker run -d -it --network=dev_bridge --name=charge_server_01 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_server_02 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_server_03 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_server_04 python-redes-image
    docker container cp \config charge_server_01:\python_redes\
    docker container cp \config charge_server_02:\python_redes\
    docker container cp \config charge_server_03:\python_redes\
    docker container cp \config charge_server_04:\python_redes\
    docker exec charge_server_01 mosquitto "-c" "/python_redes/config/mosquitto.conf" "-d"
    docker exec charge_server_02 mosquitto "-c" "/python_redes/config/mosquitto.conf" "-d"
    docker exec charge_server_03 mosquitto "-c" "/python_redes/config/mosquitto.conf" "-d"
    docker exec charge_server_04 mosquitto "-c" "/python_redes/config/mosquitto.conf" "-d"

    docker run -d -it --network=dev_bridge --name=charge_station_01 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_02 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_03 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_04 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_05 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_06 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_07 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_08 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_09 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_10 python-redes-image
)

IF "%par1%"=="stop" (

    docker container remove -f charge_station_10
    docker container remove -f charge_station_09
    docker container remove -f charge_station_08
    docker container remove -f charge_station_07
    docker container remove -f charge_station_06
    docker container remove -f charge_station_05
    docker container remove -f charge_station_04
    docker container remove -f charge_station_03
    docker container remove -f charge_station_02
    docker container remove -f charge_station_01
    docker container remove -f charge_server_04
    docker container remove -f charge_server_03
    docker container remove -f charge_server_02
    docker container remove -f charge_server_01
)

IF "%par1%"=="update" (

    docker container cp \app_python\01_server charge_server_01:/python_redes/
    docker container cp \app_python\01_server charge_server_02:/python_redes/
    docker container cp \app_python\01_server charge_server_03:/python_redes/
    docker container cp \app_python\01_server charge_server_04:/python_redes/

    docker container cp \app_python\02_station charge_station_01:/python_redes/
    docker container cp \app_python\02_station charge_station_02:/python_redes/
    docker container cp \app_python\02_station charge_station_03:/python_redes/
    docker container cp \app_python\02_station charge_station_04:/python_redes/
    docker container cp \app_python\02_station charge_station_05:/python_redes/
    docker container cp \app_python\02_station charge_station_06:/python_redes/
    docker container cp \app_python\02_station charge_station_07:/python_redes/
    docker container cp \app_python\02_station charge_station_08:/python_redes/
    docker container cp \app_python\02_station charge_station_09:/python_redes/
    docker container cp \app_python\02_station charge_station_10:/python_redes/
)

IF "%par1%"=="testdump" (
    
    docker container cp \files_test\server_01\clientdata charge_server_01:/python_redes/01_server
    docker container cp \files_test\server_01\serverdata charge_server_01:/python_redes/01_server
    docker container cp \files_test\server_02\clientdata charge_server_02:/python_redes/01_server
    docker container cp \files_test\server_02\serverdata charge_server_02:/python_redes/01_server
    docker container cp \files_test\server_03\clientdata charge_server_03:/python_redes/01_server
    docker container cp \files_test\server_03\serverdata charge_server_03:/python_redes/01_server
    docker container cp \files_test\server_04\clientdata charge_server_04:/python_redes/01_server
    docker container cp \files_test\server_04\serverdata charge_server_04:/python_redes/01_server

    docker container cp \files_test\station_01\stationdata charge_station_01:/python_redes/02_station
    docker container cp \files_test\station_02\stationdata charge_station_02:/python_redes/02_station
    docker container cp \files_test\station_03\stationdata charge_station_03:/python_redes/02_station
    docker container cp \files_test\station_04\stationdata charge_station_04:/python_redes/02_station
    docker container cp \files_test\station_05\stationdata charge_station_05:/python_redes/02_station
    docker container cp \files_test\station_06\stationdata charge_station_06:/python_redes/02_station
    docker container cp \files_test\station_07\stationdata charge_station_07:/python_redes/02_station
    docker container cp \files_test\station_08\stationdata charge_station_08:/python_redes/02_station
    docker container cp \files_test\station_09\stationdata charge_station_09:/python_redes/02_station
    docker container cp \files_test\station_10\stationdata charge_station_10:/python_redes/02_station
)

IF "%par1%"=="control" (

    IF "%par2%"=="sv01" (

        docker exec -it charge_server_01 bash
    )
    IF "%par2%"=="sv02" (

        docker exec -it charge_server_02 bash
    )
    IF "%par2%"=="sv03" (

        docker exec -it charge_server_03 bash
    )
    IF "%par2%"=="sv04" (

        docker exec -it charge_server_04 bash
    )
    IF "%par2%"=="cs01" (

        docker exec -it charge_station_01 bash
    )
    IF "%par2%"=="cs02" (

        docker exec -it charge_station_02 bash
    )
    IF "%par2%"=="cs03" (

        docker exec -it charge_station_03 bash
    )
    IF "%par2%"=="cs04" (

        docker exec -it charge_station_04 bash
    )
    IF "%par2%"=="cs05" (

        docker exec -it charge_station_05 bash
    )
    IF "%par2%"=="cs06" (

        docker exec -it charge_station_06 bash
    )
    IF "%par2%"=="cs07" (

        docker exec -it charge_station_07 bash
    )
    IF "%par2%"=="cs08" (

        docker exec -it charge_station_08 bash
    )
    IF "%par2%"=="cs09" (

        docker exec -it charge_station_09 bash
    )
    IF "%par2%"=="cs10" (

        docker exec -it charge_station_10 bash
    )
)

IF "%par1%"=="import" (

    docker container cp charge_server_01:/python_redes/01_server/clientdata \files\imported\server_01
    docker container cp charge_server_01:/python_redes/01_server/serverdata \files\imported\server_01
    docker container cp charge_server_01:/python_redes/01_server/logs \files\imported\server_01
    docker container cp charge_server_02:/python_redes/01_server/clientdata \files\imported\server_02
    docker container cp charge_server_02:/python_redes/01_server/serverdata \files\imported\server_02
    docker container cp charge_server_02:/python_redes/01_server/logs \files\imported\server_02
    docker container cp charge_server_03:/python_redes/01_server/clientdata \files\imported\server_03
    docker container cp charge_server_03:/python_redes/01_server/serverdata \files\imported\server_03
    docker container cp charge_server_03:/python_redes/01_server/logs \files\imported\server_03
    docker container cp charge_server_04:/python_redes/01_server/clientdata \files\imported\server_04
    docker container cp charge_server_04:/python_redes/01_server/serverdata \files\imported\server_04
    docker container cp charge_server_04:/python_redes/01_server/logs \files\imported\server_04

    docker container cp charge_station_01:/python_redes/02_station/stationdata \files\imported\station_01
    docker container cp charge_station_02:/python_redes/02_station/stationdata \files\imported\station_02
    docker container cp charge_station_03:/python_redes/02_station/stationdata \files\imported\station_03
    docker container cp charge_station_04:/python_redes/02_station/stationdata \files\imported\station_04
    docker container cp charge_station_05:/python_redes/02_station/stationdata \files\imported\station_05
    docker container cp charge_station_06:/python_redes/02_station/stationdata \files\imported\station_06
    docker container cp charge_station_07:/python_redes/02_station/stationdata \files\imported\station_07
    docker container cp charge_station_08:/python_redes/02_station/stationdata \files\imported\station_08
    docker container cp charge_station_09:/python_redes/02_station/stationdata \files\imported\station_09
    docker container cp charge_station_10:/python_redes/02_station/stationdata \files\imported\station_10
)

IF "%par1%"=="export" (

    docker container cp \files\export\server_01\clientdata charge_server_01:/python_redes/01_server
    docker container cp \files\export\server_01\serverdata charge_server_01:/python_redes/01_server
    docker container cp \files\export\server_01\logs charge_server_01:/python_redes/01_server
    docker container cp \files\export\server_02\clientdata charge_server_02:/python_redes/01_server
    docker container cp \files\export\server_02\serverdata charge_server_02:/python_redes/01_server
    docker container cp \files\export\server_02\logs charge_server_02:/python_redes/01_server
    docker container cp \files\export\server_03\clientdata charge_server_03:/python_redes/01_server
    docker container cp \files\export\server_03\serverdata charge_server_03:/python_redes/01_server
    docker container cp \files\export\server_03\logs charge_server_03:/python_redes/01_server
    docker container cp \files\export\server_04\clientdata charge_server_04:/python_redes/01_server
    docker container cp \files\export\server_04\serverdata charge_server_04:/python_redes/01_server
    docker container cp \files\export\server_04\logs charge_server_04:/python_redes/01_server

    docker container cp \files\export\station_01\stationdata charge_station_01:/python_redes/02_station
    docker container cp \files\export\station_02\stationdata charge_station_02:/python_redes/02_station
    docker container cp \files\export\station_03\stationdata charge_station_03:/python_redes/02_station
    docker container cp \files\export\station_04\stationdata charge_station_04:/python_redes/02_station
    docker container cp \files\export\station_05\stationdata charge_station_05:/python_redes/02_station
    docker container cp \files\export\station_06\stationdata charge_station_06:/python_redes/02_station
    docker container cp \files\export\station_07\stationdata charge_station_07:/python_redes/02_station
    docker container cp \files\export\station_08\stationdata charge_station_08:/python_redes/02_station
    docker container cp \files\export\station_09\stationdata charge_station_09:/python_redes/02_station
    docker container cp \files\export\station_10\stationdata charge_station_10:/python_redes/02_station
)

IF "%par1%"=="clearimported" (

    rmdir /s /q \files\imported\server_01\clientdata
    rmdir /s /q \files\imported\server_01\serverdata
    rmdir /s /q \files\imported\server_01\logs
    rmdir /s /q \files\imported\server_02\clientdata
    rmdir /s /q \files\imported\server_02\serverdata
    rmdir /s /q \files\imported\server_02\logs
    rmdir /s /q \files\imported\server_03\clientdata
    rmdir /s /q \files\imported\server_03\serverdata
    rmdir /s /q \files\imported\server_03\logs
    rmdir /s /q \files\imported\server_04\clientdata
    rmdir /s /q \files\imported\server_04\serverdata
    rmdir /s /q \files\imported\server_04\logs

    rmdir /s /q \files\imported\station_01\stationdata
    rmdir /s /q \files\imported\station_02\stationdata
    rmdir /s /q \files\imported\station_03\stationdata
    rmdir /s /q \files\imported\station_04\stationdata
    rmdir /s /q \files\imported\station_05\stationdata
    rmdir /s /q \files\imported\station_06\stationdata
    rmdir /s /q \files\imported\station_07\stationdata
    rmdir /s /q \files\imported\station_08\stationdata
    rmdir /s /q \files\imported\station_09\stationdata
    rmdir /s /q \files\imported\station_10\stationdata
)

IF "%par1%"=="clearexport" (

    rmdir /s /q \files\export\server_01\clientdata
    rmdir /s /q \files\export\server_01\serverdata
    rmdir /s /q \files\export\server_01\logs
    rmdir /s /q \files\export\server_02\clientdata
    rmdir /s /q \files\export\server_02\serverdata
    rmdir /s /q \files\export\server_02\logs
    rmdir /s /q \files\export\server_03\clientdata
    rmdir /s /q \files\export\server_03\serverdata
    rmdir /s /q \files\export\server_03\logs
    rmdir /s /q \files\export\server_04\clientdata
    rmdir /s /q \files\export\server_04\serverdata
    rmdir /s /q \files\export\server_04\logs
    
    rmdir /s /q \files\export\station_01\stationdata
    rmdir /s /q \files\export\station_02\stationdata
    rmdir /s /q \files\export\station_03\stationdata
    rmdir /s /q \files\export\station_04\stationdata
    rmdir /s /q \files\export\station_05\stationdata
    rmdir /s /q \files\export\station_06\stationdata
    rmdir /s /q \files\export\station_07\stationdata
    rmdir /s /q \files\export\station_08\stationdata
    rmdir /s /q \files\export\station_09\stationdata
    rmdir /s /q \files\export\station_10\stationdata
)

IF "%par1%"=="scrap" (

    docker container remove -f charge_station_10
    docker container remove -f charge_station_09
    docker container remove -f charge_station_08
    docker container remove -f charge_station_07
    docker container remove -f charge_station_06
    docker container remove -f charge_station_05
    docker container remove -f charge_station_04
    docker container remove -f charge_station_03
    docker container remove -f charge_station_02
    docker container remove -f charge_station_01
    docker container remove -f charge_server_04
    docker container remove -f charge_server_03
    docker container remove -f charge_server_02
    docker container remove -f charge_server_01
    docker network remove dev_bridge
    docker image remove python-redes-image
)