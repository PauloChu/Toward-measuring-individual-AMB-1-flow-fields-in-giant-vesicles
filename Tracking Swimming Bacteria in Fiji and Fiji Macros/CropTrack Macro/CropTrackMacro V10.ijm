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
showMessage("_Please select the folder where you wish the videos to be saved.");
savedir = getDirectory("_Choose a Directory ");

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
	cropWidth = 200;
	cropHeight = 200;
	
	// ----------------------------------------------------------------------------------------
	
	//Find number of slices
	selectImage(videoFileName);
	run("Select None");
	slices = lengthOf(posX);
	
	// Set the colour of what is left after masking
	setBackgroundColor(0, 0, 0);

	//Split stack to substacks depending on the crop field of view
	for(j=1;j<slices;j++){
		counter += 1;
		selectImage(videoFileName);
		makeRectangle(posX[j-1]-(cropWidth/2), posY[j-1]-(cropHeight/2), cropWidth, cropHeight);
		run("Make Substack...", "slices="+j+"-"+j+1);
		saveAs("Tiff", savedir+videoFileName+" Substack ("+j+"-"+(j+1)+").tif");
		close();
	}
	
	//Close original file
	selectImage(videoFileName);
	close();
	
	print((m+1) + ": "+videoList[m] + " processed.");
}

print("Batch processing completed. " + videoList.length + " videos were analyzed, " + counter + " created and saved.");

