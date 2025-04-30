if [ $1 = 'build' ]; then
    
    docker container remove -f charge_vehicle_4
    docker container remove -f charge_vehicle_3
    docker container remove -f charge_vehicle_2
    docker container remove -f charge_vehicle_1
    docker container remove -f charge_station_2
    docker container remove -f charge_station_1
    docker container remove -f charge_server
    docker network remove dev_bridge
    docker image remove python-redes-image

    docker build -t python-redes-image .
    docker network create dev_bridge
fi

if [ $1 = 'run' ]; then

    docker container remove -f charge_vehicle_4
    docker container remove -f charge_vehicle_3
    docker container remove -f charge_vehicle_2
    docker container remove -f charge_vehicle_1
    docker container remove -f charge_station_2
    docker container remove -f charge_station_1
    docker container remove -f charge_server

    docker run -d -it --network=dev_bridge --name=charge_server python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_1 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_2 python-redes-image
    docker run -d -it \
        --network=dev_bridge \
        --name=charge_vehicle_1 \
        -u=$(id -u $USER):$(id -g $USER) \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v $(pwd)/app:/app \
        python-redes-image
    docker run -d -it \
        --network=dev_bridge \
        --name=charge_vehicle_2 \
        -u=$(id -u $USER):$(id -g $USER) \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v $(pwd)/app:/app \
        python-redes-image
    docker run -d -it \
        --network=dev_bridge \
        --name=charge_vehicle_3 \
        -u=$(id -u $USER):$(id -g $USER) \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v $(pwd)/app:/app \
        python-redes-image
    docker run -d -it \
        --network=dev_bridge \
        --name=charge_vehicle_4 \
        -u=$(id -u $USER):$(id -g $USER) \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v $(pwd)/app:/app \
        python-redes-image
fi

if [ $1 = 'stop' ]; then
    
    docker container remove -f charge_vehicle_4
    docker container remove -f charge_vehicle_3
    docker container remove -f charge_vehicle_2
    docker container remove -f charge_vehicle_1
    docker container remove -f charge_station_2
    docker container remove -f charge_station_1
    docker container remove -f charge_server
fi

if [ $1 = 'update' ]; then
    
    docker container cp ./src/01_server charge_server:/python_redes/
    docker container cp ./src/02_station charge_station_1:/python_redes/
    docker container cp ./src/02_station charge_station_2:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_1:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_2:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_3:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_4:/python_redes/
fi

if [ $1 = 'control' ]; then
    
    if [ $2 = '0' ]; then
        docker exec -it charge_server bash
    fi
    if [ $2 = '1' ]; then
        docker exec -it charge_station_1 bash
    fi
    if [ $2 = '2' ]; then
        docker exec -it charge_station_2 bash
    fi
    if [ $2 = '3' ]; then
        docker exec -it charge_vehicle_1 bash
    fi
    if [ $2 = '4' ]; then
        docker exec -it charge_vehicle_2 bash
    fi
    if [ $2 = '5' ]; then
        docker exec -it charge_vehicle_3 bash
    fi
    if [ $2 = '6' ]; then
        docker exec -it charge_vehicle_4 bash
    fi
fi

if [ $1 = 'import' ]; then
    
    docker container cp charge_server:/python_redes/01_server/clientdata ./files/imported/server
    docker container cp charge_server:/python_redes/01_server/logs ./files/imported/server
    docker container cp charge_station_1:/python_redes/02_station/stationdata ./files/imported/station_1
    docker container cp charge_station_2:/python_redes/02_station/stationdata ./files/imported/station_2
    docker container cp charge_vehicle_1:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_1
    docker container cp charge_vehicle_2:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_2
    docker container cp charge_vehicle_3:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_3
    docker container cp charge_vehicle_4:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_4
fi

if [ $1 = 'export' ]; then
    
    docker container cp ./files/export/server/clientdata charge_server:/python_redes/01_server
    docker container cp ./files/export/server/logs charge_server:/python_redes/01_server
    docker container cp ./files/export/station_1/stationdata charge_station_1:/python_redes/02_station
    docker container cp ./files/export/station_2/stationdata charge_station_2:/python_redes/02_station
    docker container cp ./files/export/vehicle_1/vehicledata charge_vehicle_1:/python_redes/03_vehicle
    docker container cp ./files/export/vehicle_2/vehicledata charge_vehicle_2:/python_redes/03_vehicle
    docker container cp ./files/export/vehicle_3/vehicledata charge_vehicle_3:/python_redes/03_vehicle
    docker container cp ./files/export/vehicle_4/vehicledata charge_vehicle_4:/python_redes/03_vehicle
fi

if [ $1 = 'scrap' ]; then
    
    docker container remove -f charge_vehicle_4
    docker container remove -f charge_vehicle_3
    docker container remove -f charge_vehicle_2
    docker container remove -f charge_vehicle_1
    docker container remove -f charge_station_2
    docker container remove -f charge_station_1
    docker container remove -f charge_server
    docker network remove dev_bridge
    docker image remove python-redes-image
fi