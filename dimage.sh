for dockerfile in $(find ./services -name Dockerfile); do;  
    dir_of_image=$(dirname $dockerfile);
    image_name=$dir_of_image:t

    image_name=${image_name//\//-}
    docker_image_name="${image_name//[^a-zA-Z0-9]/-}"
    docker buildx build --platform linux/amd64,linux/arm64 -t $docker_image_name --push $dir_of_image
    done