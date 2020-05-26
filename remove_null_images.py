import os

images_dir_list = os.listdir("./images")

for one_res_image_dir in images_dir_list:
    for one_image_dir in os.listdir( "./images/" + one_res_image_dir):
        one_image_list = os.listdir("./images/" + one_res_image_dir + '/' + one_image_dir)
        for i in range(len(one_image_list)):
            if i > 30:
                try:
                    os.remove("./images/" + one_res_image_dir + '/' + one_image_dir + '/'+ str(i) + '.png')
                except:
                    pass