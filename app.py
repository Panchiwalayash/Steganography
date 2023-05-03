import os
import streamlit as st
import AdvSteganography as Steganography 
import cv2
import numpy as np

# Define Streamlit app
def app():
    # Set page title
    st.set_page_config(page_title="StegoCloud: Image Steganography App")

    # Set page heading
    st.title("Steganography App")

    parseEncoding = {"Raw":"raw", "Replicate Quadrant":'rq', "Distributed Quadrant":"dq", "Border":"b"}

    # Define function for hiding a message
    def hide_message():
        # Add file uploader for cover image
        cover_image_file = st.file_uploader("Upload a cover image", type=["jpg", "jpeg", "png"])

        # Add text input for message
        message = st.text_input("Enter message to hide")

        # Add dropdown menu for encoding technique
        encoding_options = ["Raw", "Replicate Quadrant", "Distributed Quadrant"]
        encoding = st.selectbox("Select an encoding technique", encoding_options)

        # Add hide button
        hide_button = st.button("Hide message")

        # Add text box to display result
        result_text = st.empty()

        # Handle button click
        if hide_button and cover_image_file is not None and message != "":
            # Load cover image
            cover_image = cv2.imdecode(np.frombuffer(cover_image_file.read(), np.uint8), 1)

            encoding = parseEncoding[encoding]

            # Hide message in cover image
            path = Steganography.hideMessage(originalImg=cover_image, text=message, encoding= Steganography.enType[encoding], ret=True, sl=True)
            

            result_image = cv2.imread(path)
            result_image = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB )

            # Display result image
            result_text.image(result_image)

            # check if file exists
            with open(path, "rb") as file:
                if os.path.isfile(path):
                    # add a download button
                    st.download_button(
                        label="Download Image",
                        data=file,
                        file_name="result.png",
                        mime="image/png"
                    )
                else:
                    st.write("File not found.", path)

    # Define function for hiding a message
    def hide_messageVideo():
        # Add file uploader for cover image
        cover_video_file = st.file_uploader("Upload a cover video", type=["mp4", "avi", "mov"])

        # Add text input for message
        message = st.text_input("Enter message to hide")

        # Add dropdown menu for encoding technique
        encoding_options = ["Raw", "Replicate Quadrant", "Distributed Quadrant", "Border"]
        encoding = st.selectbox("Select an encoding technique", encoding_options)

        # Add hide button
        hide_button = st.button("Hide message")

        # Handle button click
        if hide_button and cover_video_file is not None and message != "":
            # Load cover image
            input_str = str(cover_video_file)
            cover_video = cv2.VideoCapture(input_str)

            encoding = parseEncoding[encoding]

            # Hide message in cover image
            path = Steganography.hideMessageInVideo(cap=cover_video, text=message, encoding= Steganography.enType[encoding], sl=True)

            result_video = cv2.VideoCapture(path)
            print(path)

            # Display result video
            st.video(result_video)

            # add a download button
            st.download_button(
                label="Download Video",
                file_name="result.avi",
                mime="video/avi"
            )

    # Define function for reading a message
    def read_message():
        # Add file uploader for steganographic image
        steg_image_file = st.file_uploader("Upload a steganographic image", type=["jpg", "jpeg", "png"])

        # Add dropdown menu for encoding technique
        encoding_options = ["Raw", "Replicate Quadrant", "Distributed Quadrant"]
        encoding = st.selectbox("Select an encoding technique", encoding_options)

        # Add read button
        read_button = st.button("Read message")

        # Add text box to display result
        result_text = st.empty()

        # Handle button click
        if read_button and steg_image_file is not None:
            # Load steganographic image
            steg_image = cv2.imdecode(np.frombuffer(steg_image_file.read(), np.uint8), 1)
            
            # Read message from steganographic image
            encoding = parseEncoding[encoding]
            message = Steganography.readMessage(image= steg_image, encoding= Steganography.enType[encoding], ret=True)

            # Display result message
            result_text.text(message)

    def read_messageVideo():
        # Add file uploader for steganographic image
        steg_video_file = st.file_uploader("Upload a steganographic video", type=["mp4", "avi", "mov"])

        # Add dropdown menu for encoding technique
        encoding_options = ["Raw", "Replicate Quadrant", "Distributed Quadrant", "Border"]
        encoding = st.selectbox("Select an encoding technique", encoding_options)

        # Add read button
        read_button = st.button("Read message")

        # Add text box to display result
        result_text = st.empty()

        # Handle button click
        if read_button and steg_video_file is not None:
            # Load steganographic image
            steg_video = cv2.VideoCapture(steg_video_file)
            
            # Read message from steganographic image
            encoding = parseEncoding[encoding]
            message = Steganography.readMessage(image= steg_video, encoding= Steganography.enType[encoding], ret=True)

            # Display result message
            result_text.text(message)

    # Define function for about page
    def about():
        # Set page heading
        st.title("Team")
        st.subheader("Daivik Gupta and Yash Panchiwala")
        st.title("About")

        # Add text
        st.write("This steganography project allows you to hide a secret message inside an image using three encoding techniques: Raw, Replicate Quadrant, and Distributed Quadrant. The resulting output file can be downloaded in PNG or AVI format, depending on the input file type.")
        st.title("How it works")
        st.write('''The basic idea behind steganography is to hide a secret message within an innocuous-looking carrier file, such as an image or video. The message is usually hidden in the least significant bits of the carrier file, which are imperceptible to the human eye or ear.
        This project uses three encoding techniques to hide the secret message within the carrier file:

1. Raw encoding: The message is hidden in the least significant bits of the carrier file directly, without any additional processing.\n        
2. Replicate Quadrant encoding: The carrier file is divided into four quadrants, and each quadrant is replicated to hide a portion of the message.\n        
3. Distributed Quadrant encoding: The carrier file is divided into four quadrants, and each quadrant is modified to hide a portion of the message.''')
        st.title("Usage")
        st.write('To use this steganography project, simply select an input file (image), choose an encoding technique, and enter the secret message you want to hide. Then click the "Hide" button to generate the output file.If you want to view the hidden message, simply select the output file and click the "Read" button. The secret message will be displayed in the text box.')

    # Define page navigation
    pages = {
        "Hide message": hide_message,
        "Read message": read_message,
        # "Hide message (for Video)": hide_messageVideo,
        # "Read message (for Video)": read_messageVideo,
        "About": about,
    }
    page = st.sidebar.selectbox("Select a page", tuple(pages.keys()))

    # Display selected page
    pages[page]()

app()
