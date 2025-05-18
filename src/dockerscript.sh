if [ $1 = 'build' ]; then
    
    docker container remove -f electric_vehicle_04
    docker container remove -f electric_vehicle_03
    docker container remove -f electric_vehicle_02
    docker container remove -f electric_vehicle_01
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
fi

if [ $1 = 'saveimage' ]; then
    
    docker save python-redes-image:latest -o python-redes-image.tar
fi

if [ $1 = 'loadimage' ]; then
    
    docker container remove -f electric_vehicle_04
    docker container remove -f electric_vehicle_03
    docker container remove -f electric_vehicle_02
    docker container remove -f electric_vehicle_01
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
fi

if [ $1 = 'run' ]; then

    docker container remove -f electric_vehicle_04
    docker container remove -f electric_vehicle_03
    docker container remove -f electric_vehicle_02
    docker container remove -f electric_vehicle_01
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
    docker container cp ./config charge_server_01:/python_redes/
    docker container cp ./config charge_server_02:/python_redes/
    docker container cp ./config charge_server_03:/python_redes/
    docker container cp ./config charge_server_04:/python_redes/
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
    
    docker run -d -it \
        --network=dev_bridge \
        --name=electric_vehicle_01 \
        -u=$(id -u $USER):$(id -g $USER) \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v $(pwd)/app:/app \
        python-redes-image
    docker run -d -it \
        --network=dev_bridge \
        --name=electric_vehicle_02 \
        -u=$(id -u $USER):$(id -g $USER) \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v $(pwd)/app:/app \
        python-redes-image
    docker run -d -it \
        --network=dev_bridge \
        --name=electric_vehicle_03 \
        -u=$(id -u $USER):$(id -g $USER) \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v $(pwd)/app:/app \
        python-redes-image
    docker run -d -it \
        --network=dev_bridge \
        --name=electric_vehicle_04 \
        -u=$(id -u $USER):$(id -g $USER) \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v $(pwd)/app:/app \
        python-redes-image
fi

if [ $1 = 'stop' ]; then
    
    docker container remove -f electric_vehicle_04
    docker container remove -f electric_vehicle_03
    docker container remove -f electric_vehicle_02
    docker container remove -f electric_vehicle_01
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
fi

if [ $1 = 'update' ]; then
    
    docker container cp ./app_python/01_server charge_server_01:/python_redes/
    docker container cp ./app_python/01_server charge_server_02:/python_redes/
    docker container cp ./app_python/01_server charge_server_03:/python_redes/
    docker container cp ./app_python/01_server charge_server_04:/python_redes/

    docker container cp ./app_python/02_station charge_station_01:/python_redes/
    docker container cp ./app_python/02_station charge_station_02:/python_redes/
    docker container cp ./app_python/02_station charge_station_03:/python_redes/
    docker container cp ./app_python/02_station charge_station_04:/python_redes/
    docker container cp ./app_python/02_station charge_station_05:/python_redes/
    docker container cp ./app_python/02_station charge_station_06:/python_redes/
    docker container cp ./app_python/02_station charge_station_07:/python_redes/
    docker container cp ./app_python/02_station charge_station_08:/python_redes/
    docker container cp ./app_python/02_station charge_station_09:/python_redes/
    docker container cp ./app_python/02_station charge_station_10:/python_redes/

    docker container cp ./app_python/03_vehicle electric_vehicle_01:/python_redes/
    docker container cp ./app_python/03_vehicle electric_vehicle_02:/python_redes/
    docker container cp ./app_python/03_vehicle electric_vehicle_03:/python_redes/
    docker container cp ./app_python/03_vehicle electric_vehicle_04:/python_redes/
fi

if [ $1 = 'testdump' ]; then
    
    docker container cp ./files_test/server_01/clientdata charge_server_01:/python_redes/01_server
    docker container cp ./files_test/server_01/serverdata charge_server_01:/python_redes/01_server
    docker container cp ./files_test/server_02/clientdata charge_server_02:/python_redes/01_server
    docker container cp ./files_test/server_02/serverdata charge_server_02:/python_redes/01_server
    docker container cp ./files_test/server_03/clientdata charge_server_03:/python_redes/01_server
    docker container cp ./files_test/server_03/serverdata charge_server_03:/python_redes/01_server
    docker container cp ./files_test/server_04/clientdata charge_server_04:/python_redes/01_server
    docker container cp ./files_test/server_04/serverdata charge_server_04:/python_redes/01_server
    docker container cp ./test charge_server_01:/python_redes/
    docker container cp ./test charge_server_02:/python_redes/
    docker container cp ./test charge_server_03:/python_redes/
    docker container cp ./test charge_server_04:/python_redes/


    docker container cp ./files_test/station_01/stationdata charge_station_01:/python_redes/02_station
    docker container cp ./files_test/station_02/stationdata charge_station_02:/python_redes/02_station
    docker container cp ./files_test/station_03/stationdata charge_station_03:/python_redes/02_station
    docker container cp ./files_test/station_04/stationdata charge_station_04:/python_redes/02_station
    docker container cp ./files_test/station_05/stationdata charge_station_05:/python_redes/02_station
    docker container cp ./files_test/station_06/stationdata charge_station_06:/python_redes/02_station
    docker container cp ./files_test/station_07/stationdata charge_station_07:/python_redes/02_station
    docker container cp ./files_test/station_08/stationdata charge_station_08:/python_redes/02_station
    docker container cp ./files_test/station_09/stationdata charge_station_09:/python_redes/02_station
    docker container cp ./files_test/station_10/stationdata charge_station_10:/python_redes/02_station

    docker container cp ./files_test/vehicle_01/vehicledata electric_vehicle_01:/python_redes/03_vehicle
    docker container cp ./files_test/vehicle_02/vehicledata electric_vehicle_02:/python_redes/03_vehicle
    docker container cp ./files_test/vehicle_03/vehicledata electric_vehicle_03:/python_redes/03_vehicle
    docker container cp ./files_test/vehicle_04/vehicledata electric_vehicle_04:/python_redes/03_vehicle
fi

if [ $1 = 'control' ]; then
    
    if [ $2 = 'sv01' ]; then
        docker exec -it charge_server_01 bash
    fi
    if [ $2 = 'sv02' ]; then
        docker exec -it charge_server_02 bash
    fi
    if [ $2 = 'sv03' ]; then
        docker exec -it charge_server_03 bash
    fi
    if [ $2 = 'sv04' ]; then
        docker exec -it charge_server_04 bash
    fi
    if [ $2 = 'cs01' ]; then
        docker exec -it charge_station_01 bash
    fi
    if [ $2 = 'cs02' ]; then
        docker exec -it charge_station_02 bash
    fi
    if [ $2 = 'cs03' ]; then
        docker exec -it charge_station_03 bash
    fi
    if [ $2 = 'cs04' ]; then
        docker exec -it charge_station_04 bash
    fi
    if [ $2 = 'cs05' ]; then
        docker exec -it charge_station_05 bash
    fi
    if [ $2 = 'cs06' ]; then
        docker exec -it charge_station_06 bash
    fi
    if [ $2 = 'cs07' ]; then
        docker exec -it charge_station_07 bash
    fi
    if [ $2 = 'cs08' ]; then
        docker exec -it charge_station_08 bash
    fi
    if [ $2 = 'cs09' ]; then
        docker exec -it charge_station_09 bash
    fi
    if [ $2 = 'cs10' ]; then
        docker exec -it charge_station_10 bash
    fi
    if [ $2 = 'ev01' ]; then
        docker exec -it electric_vehicle_01 bash
    fi
    if [ $2 = 'ev02' ]; then
        docker exec -it electric_vehicle_02 bash
    fi
    if [ $2 = 'ev03' ]; then
        docker exec -it electric_vehicle_03 bash
    fi
    if [ $2 = 'ev04' ]; then
        docker exec -it electric_vehicle_04 bash
    fi
fi

if [ $1 = 'import' ]; then
    
    docker container cp charge_server_01:/python_redes/01_server/clientdata ./files/imported/server_01
    docker container cp charge_server_01:/python_redes/01_server/serverdata ./files/imported/server_01
    docker container cp charge_server_01:/python_redes/01_server/logs ./files/imported/server_01
    docker container cp charge_server_02:/python_redes/01_server/clientdata ./files/imported/server_02
    docker container cp charge_server_02:/python_redes/01_server/serverdata ./files/imported/server_02
    docker container cp charge_server_02:/python_redes/01_server/logs ./files/imported/server_02
    docker container cp charge_server_03:/python_redes/01_server/clientdata ./files/imported/server_03
    docker container cp charge_server_03:/python_redes/01_server/serverdata ./files/imported/server_03
    docker container cp charge_server_03:/python_redes/01_server/logs ./files/imported/server_03
    docker container cp charge_server_04:/python_redes/01_server/clientdata ./files/imported/server_04
    docker container cp charge_server_04:/python_redes/01_server/serverdata ./files/imported/server_04
    docker container cp charge_server_04:/python_redes/01_server/logs ./files/imported/server_04

    docker container cp charge_station_01:/python_redes/02_station/stationdata ./files/imported/station_01
    docker container cp charge_station_02:/python_redes/02_station/stationdata ./files/imported/station_02
    docker container cp charge_station_03:/python_redes/02_station/stationdata ./files/imported/station_03
    docker container cp charge_station_04:/python_redes/02_station/stationdata ./files/imported/station_04
    docker container cp charge_station_05:/python_redes/02_station/stationdata ./files/imported/station_05
    docker container cp charge_station_06:/python_redes/02_station/stationdata ./files/imported/station_06
    docker container cp charge_station_07:/python_redes/02_station/stationdata ./files/imported/station_07
    docker container cp charge_station_08:/python_redes/02_station/stationdata ./files/imported/station_08
    docker container cp charge_station_09:/python_redes/02_station/stationdata ./files/imported/station_09
    docker container cp charge_station_10:/python_redes/02_station/stationdata ./files/imported/station_10

    docker container cp electric_vehicle_01:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_01
    docker container cp electric_vehicle_02:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_02
    docker container cp electric_vehicle_03:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_03
    docker container cp electric_vehicle_04:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_04
fi

if [ $1 = 'export' ]; then
    
    docker container cp ./files/export/server_01/clientdata charge_server_01:/python_redes/01_server
    docker container cp ./files/export/server_01/serverdata charge_server_01:/python_redes/01_server
    docker container cp ./files/export/server_01/logs charge_server_01:/python_redes/01_server
    docker container cp ./files/export/server_02/clientdata charge_server_02:/python_redes/01_server
    docker container cp ./files/export/server_02/serverdata charge_server_02:/python_redes/01_server
    docker container cp ./files/export/server_02/logs charge_server_02:/python_redes/01_server
    docker container cp ./files/export/server_03/clientdata charge_server_03:/python_redes/01_server
    docker container cp ./files/export/server_03/serverdata charge_server_03:/python_redes/01_server
    docker container cp ./files/export/server_03/logs charge_server_03:/python_redes/01_server
    docker container cp ./files/export/server_04/clientdata charge_server_04:/python_redes/01_server
    docker container cp ./files/export/server_04/serverdata charge_server_04:/python_redes/01_server
    docker container cp ./files/export/server_04/logs charge_server_04:/python_redes/01_server
    
    docker container cp ./files/export/station_01/stationdata charge_station_01:/python_redes/02_station
    docker container cp ./files/export/station_02/stationdata charge_station_02:/python_redes/02_station
    docker container cp ./files/export/station_03/stationdata charge_station_03:/python_redes/02_station
    docker container cp ./files/export/station_04/stationdata charge_station_04:/python_redes/02_station
    docker container cp ./files/export/station_05/stationdata charge_station_05:/python_redes/02_station
    docker container cp ./files/export/station_06/stationdata charge_station_06:/python_redes/02_station
    docker container cp ./files/export/station_07/stationdata charge_station_07:/python_redes/02_station
    docker container cp ./files/export/station_08/stationdata charge_station_08:/python_redes/02_station
    docker container cp ./files/export/station_09/stationdata charge_station_09:/python_redes/02_station
    docker container cp ./files/export/station_10/stationdata charge_station_10:/python_redes/02_station

    docker container cp ./files/export/vehicle_01/vehicledata electric_vehicle_01:/python_redes/03_vehicle
    docker container cp ./files/export/vehicle_02/vehicledata electric_vehicle_02:/python_redes/03_vehicle
    docker container cp ./files/export/vehicle_03/vehicledata electric_vehicle_03:/python_redes/03_vehicle
    docker container cp ./files/export/vehicle_04/vehicledata electric_vehicle_04:/python_redes/03_vehicle
fi

if [ $1 = 'clearimported' ]; then
    
    rm -r ./files/imported/server_01/clientdata
    rm -r ./files/imported/server_01/serverdata
    rm -r ./files/imported/server_01/logs
    rm -r ./files/imported/server_02/clientdata
    rm -r ./files/imported/server_02/serverdata
    rm -r ./files/imported/server_02/logs
    rm -r ./files/imported/server_03/clientdata
    rm -r ./files/imported/server_03/serverdata
    rm -r ./files/imported/server_03/logs
    rm -r ./files/imported/server_04/clientdata
    rm -r ./files/imported/server_04/serverdata
    rm -r ./files/imported/server_04/logs

    rm -r ./files/imported/station_01/stationdata
    rm -r ./files/imported/station_02/stationdata
    rm -r ./files/imported/station_03/stationdata
    rm -r ./files/imported/station_04/stationdata
    rm -r ./files/imported/station_05/stationdata
    rm -r ./files/imported/station_06/stationdata
    rm -r ./files/imported/station_07/stationdata
    rm -r ./files/imported/station_08/stationdata
    rm -r ./files/imported/station_09/stationdata
    rm -r ./files/imported/station_10/stationdata

    rm -r ./files/imported/vehicle_01/vehicledata
    rm -r ./files/imported/vehicle_02/vehicledata
    rm -r ./files/imported/vehicle_03/vehicledata
    rm -r ./files/imported/vehicle_04/vehicledata
fi

if [ $1 = 'clearexport' ]; then
    
    rm -r ./files/export/server_01/clientdata
    rm -r ./files/export/server_01/serverdata
    rm -r ./files/export/server_01/logs
    rm -r ./files/export/server_02/clientdata
    rm -r ./files/export/server_02/serverdata
    rm -r ./files/export/server_02/logs
    rm -r ./files/export/server_03/clientdata
    rm -r ./files/export/server_03/serverdata
    rm -r ./files/export/server_03/logs
    rm -r ./files/export/server_04/clientdata
    rm -r ./files/export/server_04/serverdata
    rm -r ./files/export/server_04/logs

    rm -r ./files/export/station_01/stationdata
    rm -r ./files/export/station_02/stationdata
    rm -r ./files/export/station_03/stationdata
    rm -r ./files/export/station_04/stationdata
    rm -r ./files/export/station_05/stationdata
    rm -r ./files/export/station_06/stationdata
    rm -r ./files/export/station_07/stationdata
    rm -r ./files/export/station_08/stationdata
    rm -r ./files/export/station_09/stationdata
    rm -r ./files/export/station_10/stationdata

    rm -r ./files/export/vehicle_01/vehicledata
    rm -r ./files/export/vehicle_02/vehicledata
    rm -r ./files/export/vehicle_03/vehicledata
    rm -r ./files/export/vehicle_04/vehicledata
fi

if [ $1 = 'scrap' ]; then
    
    docker container remove -f electric_vehicle_04
    docker container remove -f electric_vehicle_03
    docker container remove -f electric_vehicle_02
    docker container remove -f electric_vehicle_01
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
fi