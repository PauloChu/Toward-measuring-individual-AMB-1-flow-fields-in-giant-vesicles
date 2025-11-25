//Prompt user to open the folder with the video files and then the CSV files
showMessage("Please select the folder you wish to process.");
dir = getDirectory("Choose a Directory ");
savdir = dir;
fileList = getFileList(dir);
videoList = newArray()

//Variable that counts how many videos are created
counter = 0;

//Create an array with all of the video file names
for (i=0; i<fileList.length; i++) {
	if (endsWith(fileList[i], ".csv"))
		{}
	else{
		videoList = Array.concat(videoList, fileList[i]);
		}
}

//Start process for every video
for(m=0; m<videoList.length; m++){
	
	//Open the video file
	videoFileName = videoList[m];
	open(dir+videoFileName);
	
	run("Z Project...", "projection=Median");
	
	imageCalculator("Subtract stack", videoFileName ,"MED_"+videoFileName);
	selectImage("MED_"+videoFileName);
	close;
	selectImage(videoFileName);
	run("Despeckle", "stack");
	saveAs("Tiff", savdir+videoFileName);
	close;
	
	print((m+1) + ": "+ videoFileName + " processed.");
}

print("Batch processing completed. " + videoList.length + " videos were processed and saved.");


