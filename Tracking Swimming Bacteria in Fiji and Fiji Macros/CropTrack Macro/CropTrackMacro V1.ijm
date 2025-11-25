//Open the video file
videoFile = File.openDialog("Choose your video file");
videoFileSplit = split(videoFile,"/")
videoFileName = videoFileSplit[videoFileSplit.length-1];
open(videoFile)

// ----------------------------------------------------------------------------------------

//Open CSV as string
file = File.openDialog("Select the CSV file corresponding to the video");
fileSplit = split(file,"/");
fileName = fileSplit[fileSplit.length-1];
folder = String.join(Array.deleteValue(fileSplit,fileName), "/");
x = File.openAsString("/"+folder+"/"+fileName);

//Get File List
fileList = getFileList(folder);

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

//Separate stack to individual images
selectImage(videoFileName);
slices = nSlices();
run("Stack to Images");


// Cycle through each image and crop
imageName = getInfo("image.title");
imageNameSplit = split(imageName,"-");
imageNameBase = String.join(Array.deleteValue(imageNameSplit,imageNameSplit[imageNameSplit.length-1]), "-");
for(k=1;k<slices+1;k++){
	sliceNumber = "0000" + k;
	kStr = "" + k;
	sliceNumber = substring(sliceNumber,kStr.length);
	selectImage(imageNameBase+"-"+sliceNumber);
	makeRectangle(posX[k-1]-(cropWidth/2), posY[k-1]-(cropHeight/2), cropWidth, cropHeight);
	run("Crop");
}

//Combine all of the images back to a stack
run("Images to Stack", "  title="+imageNameBase+" use");

