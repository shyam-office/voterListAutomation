from django.shortcuts import render
from django.conf import settings
import gc
import os
import cv2
import pytesseract
from pdf2image import convert_from_path
from langdetect import detect

# Create your views here.
class PdfProcessing:

    path_to_process = settings.MEDIA_ROOT + '/pdfimages/'
    lang = 'en'

    def __init__(self):
        print("PdfProcessing init => ", self.path_to_process)

    @classmethod
    def process_each_page(self, fileName):
        pass


    @classmethod
    def read_pdf(self, pdf_file_name):
        # print('read_pdf: ', self, pdf_file_name)
        file_format = 'csv'

        outFile = settings.MEDIA_ROOT + '/uploads/temp.' + file_format

        f = open(outFile, "a")

        self.split_images_from_image_pdf(pdf_file_name)

        lan_detection_path = 'page_1.jpg'
        self.detect_language(lan_detection_path)

        self.process_image_pdf()
        pass

    @classmethod
    def split_images_from_image_pdf(self, pdf_file_name):
        gc.collect() # python garbage collector
        # Store all the pages of the PDF in a variable 
        pages = convert_from_path(pdf_file_name, 500)
        # print(psutil.virtual_memory())

        # Counter to store images of each page of PDF to image 
        self.image_counter = 1

        # Iterate through all the pages stored above 
        for page in pages: 
            # Declaring filename for each page of PDF as JPG 
            # For each page, filename will be: 
            # PDF page 1 -> page_1.jpg 
            # PDF page 2 -> page_2.jpg 
            # PDF page 3 -> page_3.jpg 
            # .... 
            # PDF page n -> page_n.jpg 
            filename = "page_"+str(self.image_counter)+".jpg"

            # Save the image of the page in system 
            page.save(os.path.join(self.path_to_process, filename), 'JPEG') 

            # Increment the counter to update filename 
            self.image_counter = self.image_counter + 1


    @classmethod
    def detect_language(self, file_name): #"page_1.jpg"
        """Detect language and pass to relevant routine"""

        self.lang = "eng"
        #  translator = Translator()
        imPath = file_name

        # Define config parameters.
        # '-l eng'  for using the English language
        # '--oem 1' for using LSTM OCR Engine
        # config = ('-l mar+hin+ben+eng+tam --oem 1 --psm 3') #+hin 
        config = ('-l tam+guj+eng+pan+ben+tel+kan+asm+hin+mar --oem 1 --psm 3')
        print("Detect Language >>>>>>1")
        
        try:
            f = open(self.path_to_process+imPath)
            print("path_to_process", self.path_to_process+imPath)
            print("File path",f)
        except IOError:
            print("File not accessible")
        finally:
            f.close()
        # Read image from disk
        im = cv2.imread(self.path_to_process + imPath, cv2.IMREAD_COLOR)
        print("Detect Language >>>>>>2")
        # Run tesseract OCR on image
        text = pytesseract.image_to_string(im, config=config)
        # print("detect_language (Text)>>", text)
        print("Detect Language >>>>>>3")
        # using langdetect
        
        print("detect_language (Lang)>>", detect(text))

        if detect(text) == 'hi':
            self.lang = "hin+eng"
            self.transliteration_lang = 'hin'
        elif detect(text) == 'mr':
            self.lang = "mar"
            self.transliteration_lang = 'mar'
        elif detect(text) == 'bn':
            self.lang = "ben"
            self.transliteration_lang = 'ben'
        elif detect(text) == 'ta':
            self.lang = "tam"
            self.transliteration_lang = 'tam'
        elif detect(text) == 'te':
            self.lang = "tel"
            self.transliteration_lang = 'tel'
        elif detect(text) == 'pa':
            self.lang = "pan"
            self.transliteration_lang = 'pan'
        elif detect(text) == 'gu':
            self.lang = "guj"
            self.transliteration_lang = 'guj'

        print("detect_language (Lang)>> {}\ntransliteration_lang: {}".format(self.lang, self.transliteration_lang))


    @classmethod
    def process_image_pdf(self):
        """Process each pages of image pdf"""
        print('process_image_pdf, image_counter =', self.image_counter)
        # return render_template('single_imagepdf.html', slno = "I'm here:with i" )
        for cnt in range(1, self.image_counter):
            print('cnt = ' + str(cnt))
            self.process_each_page("page_"+str(cnt)+ ".jpg")

    
    @classmethod
    def process_each_page(self, file_name):
        filename, file_extension = os.path.splitext(file_name)
        print('process_each_page >> filename = ', filename)
        # Crop the outer tables only
        return_val = self.extract_outer_tables(file_name)

        print("return val: ", return_val)
    

    @classmethod
    def extract_outer_tables(self, file_name):
        """To extract the table part of the image. 
        The outer table is considered, i.e. the boundary within which all voter's data is present. 
        Returns: number of outer tables found --> (int)
        """
        filename, file_extension = os.path.splitext(file_name)
        print('extract_outer_tables >> filename=', filename)

        # Read input image
        img = cv2.imread(self.path_to_process+file_name, cv2.IMREAD_COLOR)

        # Convert to gray scale image
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # Simple threshold
        _, thr = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        # Morphological closing to improve mask
        close = cv2.morphologyEx(255 - thr, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))

        # Find only outer contours
        contours, _ = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Save images for large enough contours
        areaThr = 200000
        i = 0
        print('contours1 = ', len(contours))
        rects = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, width, height = cv2.boundingRect(cnt)
            print('dimensions = ', x, y, width, height)
            area = width*height
            print('new area = ', area, areaThr, area > areaThr) 
            if (area > areaThr):
                i = i + 1
                new_filename = filename + "_outer_table_" + str(i) + file_extension
                # new_filename = filename + "_outer_table" + '.jpg'
                print('---------------------')
                print('area in extract_outer_tables = ', area)
                print ('i =', i)
                print('area = ', area)
                print('extract_outer_tables >> new_filename =', new_filename)
                print('---------------------')
                cv2.imwrite(self.path_to_process + new_filename, img[y:y+height-1, x:x+width-1])
                #------------------
                rect = (x, y, width, height)
                rects.append(rect)
                
        # =============================================================================
        # print('[cnt] = ', [cnt])
        # cv2.drawContours(mask, [cnt], -1, 0, -1)
        # remove the contours from the image and show the resulting images
        # image = cv2.bitwise_and(img, img, mask=mask)
        # =============================================================================

        # to save the image without the table.
        if i > 0:
            new_filename = filename + "_without_outer_table" +  file_extension
            print ('i =', i)
            print('extract_outer_tables >> new_filename =' , new_filename)
            # =============================================================================
            # cv2.imwrite(self.path_to_process + new_filename, img)
            # img = cv2.imread(self.path_to_process + new_filename, cv2.IMREAD_COLOR)
            # =============================================================================

            print('rects = ', rects)
            j = 0
            for x, y, w, h in rects:
                print('j = ', j)
                print(x, y, w, h)
                j = j + 1
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), -1)

            cv2.imwrite(self.path_to_process + new_filename, img)

        return i