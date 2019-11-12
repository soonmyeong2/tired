import argparse


def main():
    parser = argparse.ArgumentParser(description='Sleep time check program')
    parser.add_argument('course_key', type=str, help="Input course_key")
    parser.add_argument('email', type=str, help="Input email")
    args = parser.parse_args()

    #direct = Path(os.path.expanduser('~'))
    #file_path = direct / args.img_file
    #img = cv2.imread(str(file_path))
    
    #print(" #pirnt image file path : " + str(file_path)) 
    
    #if args.option:
    #    select_freset(args.option, img)
    #else:
    #    default_freset(args.natural, args.noise, args.text_boxes, img)


if __name__ == "__main__":
    main()
