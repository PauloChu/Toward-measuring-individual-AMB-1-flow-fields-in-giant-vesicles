//Prompt user to open the folder with the video files and then the CSV files
showMessage("Please select the folder you wish to process.");
dir = getDirectory("Choose a Directory ");
folderList = getFileList(dir);
print(folderList[0]);

for(j=0; j<folderList.length; j++){

	savdir = dir + folderList[j];
	fileList = getFileList(dir + folderList[j]);
	videoList = newArray();
	
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
		open(dir+folderList[j]+videoFileName);
		
		run("Make Binary", "calculate black");
		run("Watershed", "stack");
		
		// Set measurements to measure (center of ROI)
		run("Set Measurements...", "area mean min centroid center stack redirect=None decimal=3");
		
		// Analyze ROIs of particles
		run("Analyze Particles...", "clear add stack");
		
		// Delete all info in stacks
		run("Select All");
		run("Clear", "stack");
		
		// Select all of the ROIs and find their centers
		roiManager("Deselect");
		roiManager("Measure");
		
		for(var i=1; i < nResults;i++) { 
			// Get position of centroidf
			x = getResult("X", i - 1);
			y = getResult("Y", i - 1);
			toUnscaled(x, y);
			slice = getResult("Slice", i - 1);
			selectImage(videoFileName);
			// Set Slice
			setSlice(parseInt(slice));
			// Make an inverted square centered at center
			makeRectangle(x-1, y-1, 3, 3);
			run("Invert", "slice");
		}
		
		roiManager("Deselect");
		roiManager("Delete");
		close("ROI Manager");
		close("Results");
		
		saveAs("Tiff", savdir+videoFileName);
		close;
		
		print((m+1) + ": "+ videoFileName + " processed.");
	}
	
	print("Batch processing completed. " + videoList.length + " videos were processed and saved.");
}
