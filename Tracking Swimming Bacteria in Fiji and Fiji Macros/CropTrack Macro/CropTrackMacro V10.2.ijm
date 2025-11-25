//Prompt user to open the folder with the video files and then the CSV files
showMessage("Please select the folder of folders you wish to process.");
dir = getDirectory("Choose a Directory ");
folders = getFileList(dir)

showMessage("_Please select the folder where you wish the folders of videos to be saved.");
savedir = getDirectory("_Choose a Directory ");

for(i=0;i<folders.length;i++) {
		
	File.openSequence(dir+"/"+folders[i]);
	
	File.makeDirectory(savedir+folders[i])
	
	//Variable that counts how many videos are created
	counter = 0;
	
	//Prompt user to open the folder where the videos will be saved

	
	//Find number of slices
	videoFileName = getTitle;
	selectImage(videoFileName);
	cropHeight = getHeight();
	cropWidth = getWidth();
	slices = nSlices();
	
	//Split stack to substacks depending on the crop field of view
	for(j=1;j<slices;j++){
		counter += 1;
		selectImage(videoFileName);
		makeRectangle(0, 0, cropWidth, cropHeight);
		run("Make Substack...", "slices="+j+"-"+j+1);
		saveAs("Tiff", savedir+folders[i]+videoFileName+" Substack ("+j+"-"+(j+1)+").tif");
		close();
	}
	
	//Close original file
	selectImage(videoFileName);
	close();
	
	print(counter + " videos created and saved. " + folders[i] + " completed.");
}
print("All done!");

