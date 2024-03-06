for dockerfile in $(find ./services -name Dockerfile); do
    code $dockerfile
    dir_of_image=$(dirname $dockerfile)
    last_folder=$(basename $dir_of_image)
    
    # echo "Building $dir_of_image"
    image_name=$last_folder
    # echo "Building $image_name"

    image_name=${image_name//\//-}
    docker_image_name="${image_name//[^a-zA-Z0-9]/-}"
    echo "Building $docker_image_name"
    # docker buildx build --platform linux/amd64,linux/arm64 -t $docker_image_name --push $dir_of_image
    done