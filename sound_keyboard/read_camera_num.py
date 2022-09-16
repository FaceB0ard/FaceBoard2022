def read_camera_num():
    camera_num = 0
    try:
        with open("camera_num.txt", "r") as f:
            camera_num = int(f.read())
    except:
        pass
    return camera_num

if __name__ == "__main__":
    print(read_camera_num())