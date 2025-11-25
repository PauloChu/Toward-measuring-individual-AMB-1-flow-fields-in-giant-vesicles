//Prompt user to open the folder with the video files and then the CSV files
showMessage("Please select the folder you wish to process.");
dir = getDirectory("Choose a Directory ");
fileList = getFileList(dir);
videoList = newArray()
CSVList = newArray()

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

//Prompt user to open the folder where the videos will be saved
showMessage("Please select the folder where you wish the videos to be saved.");
savedir = getDirectory("Choose a Directory ");

//Start process for every video
for(m=0; m<videoList.length; m++){
	
	//Open the video file
	videoFileName = videoList[m];
	open(dir+videoList[m]);
	
	// ----------------------------------------------------------------------------------------
	
	//Open CSV as string
	fileSplit = split(videoList[m],".");
	fileCSV = String.join(Array.deleteValue(fileSplit,"tif"), ".");
	fileCSV = "Results " + fileCSV + ".csv";
	x = File.openAsString(dir+fileCSV);
	
	//Separate file into rows
	rows = split(x,"\n");
	
	//Find row with the Header Names
	rowNames = rows[0];
	rowName = split(rowNames,",");
	
	//Get X and Y location of the Track at each point
	posX = newArray();
	posY = newArray();
	for(i=1;i<rows.length; i++){
		rowDataPoints = split(rows[i],",");
		posX = Array.concat(posX,rowDataPoints[2]);
		posY = Array.concat(posY,rowDataPoints[3]);
	}
	
	//Define Width and Height of the crop
	cropWidth = 120;
	cropHeight = 120;
	y_centering = 0.45; // How far up the video the MTB is centered (0.5 = centered)
	
	// ----------------------------------------------------------------------------------------
	
	//Find number of slices
	selectImage(videoFileName);
	run("Select None");
	slices = nSlices();
	
	// Cycle through each slice and determine crop space
	cropThreshold = parseInt(posY[0]) + 1;
	substacks = newArray();
	crop_points = newArray();
	for(k=1;k<slices+1;k++){
		if(parseFloat(posY[k-1]) < parseFloat(cropThreshold)){
			crop_points = Array.concat(crop_points, newArray(parseFloat(posX[k-1])-(cropWidth/2), parseFloat(posY[k-1])-(cropHeight*(1-y_centering))));
			cropThreshold = parseInt(posY[k-1]) - 19; // 19 pixels = 2 microns
			substacks = Array.concat(substacks,k);
			counter += 1;
		}
	}
	
	//Add the last frame to the substacks array if not already added.
	if(substacks[substacks.length-1] != k-1){
		substacks = Array.concat(substacks,k-1);
	}
	
	
	//Split stack to substacks depending on the crop field of view
	for(j=1;j<substacks.length;j++){
		selectImage(videoFileName);
		run("Make Substack...", "slices="+substacks[j-1]+"-"+substacks[j]);
		
		makeRectangle(crop_points[(j-1)*2], crop_points[(j-1)*2+1], cropWidth, cropHeight);
		run("Crop");
	}
	
	//Close original file
	selectImage(videoFileName);
	close();
	
	for(j=1;j<substacks.length;j++){
		selectImage("Substack ("+substacks[j-1]+"-"+substacks[j]+")");
		run("AVI... ", "compression=JPEG frame=25 save=["+savedir+videoFileName+" Substack ("+substacks[j-1]+"-"+substacks[j]+").avi]");
		selectImage("Substack ("+substacks[j-1]+"-"+substacks[j]+")");
		close();
	}
	
	print(videoList[m] + " processed.");
}

print("Batch processing completed. " + counter + " videos were created and saved.");

