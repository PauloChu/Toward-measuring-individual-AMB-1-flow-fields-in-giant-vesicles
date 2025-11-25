//Prompt user to open video file and then the CSV file
showMessage("Please first select the video you wish to process and then open the corresponding CSV with the tracking information.");

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
cropWidth = 120;
cropHeight = 120;
y_centering = 0.45; // How far up the video the MTB is centered (0.5 = centered)

// ----------------------------------------------------------------------------------------

//Calculate the correction angle at which to rotate the image after cropping

cropping_angle = newArray(); 			//This variable stores at which angle to rotate for each position
cropping_angle_substack = newArray(); 	//This variable stores at which angle to rotate for each substack
normal_vector = newArray(0,1);

function getAngle(vec1, vec2){
	dot_product = (vec1[0] * vec2[0]) + (- vec1[1] * vec2[1]);
	magnitude_product = Math.sqrt(Math.sqr(vec1[0]) + Math.sqr(vec1[1])) * Math.sqrt(Math.sqr(vec2[0]) + Math.sqr(vec2[1]));
	return Math.acos((dot_product / magnitude_product)) * (180 / PI);
}

for(m=1;m<posX.length;m++){
	if(m > posX.length - 5){
		direction_vector = newArray(parseFloat(posX[posX.length-1]) - parseFloat(posX[m-2]), parseFloat(posY[posY.length-1]) - parseFloat(posY[m-2]));
		cropping_angle = Array.concat(cropping_angle,getAngle(normal_vector, direction_vector));
		print(cropping_angle[m-1]);
	}
	else {
		direction_vector = newArray(parseFloat(posX[m+4]) - parseFloat(posX[m-1]), parseFloat(posY[m+4]) - parseFloat(posY[m-1]));
		cropping_angle = Array.concat(cropping_angle,getAngle(normal_vector, direction_vector));
		print(cropping_angle[m-1]);
	}
}

// ----------------------------------------------------------------------------------------

//Separate stack to individual images
selectImage(videoFileName);
slices = nSlices();
run("Stack to Images");


// Cycle through each image and crop
imageName = getInfo("image.title");
imageNameSplit = split(imageName,"-");
imageNameBase = String.join(Array.deleteValue(imageNameSplit,imageNameSplit[imageNameSplit.length-1]), "-");
cropThreshold = parseInt(posY[0]) + 1;
substacks = newArray();
for(k=1;k<slices+1;k++){
	if(parseFloat(posY[k-1]) < parseFloat(cropThreshold)){
//		print("Threshold reached...");
//		print("Slice: "+ (k-1));
//		print("Y Position: " + posY[k-1]);
//		print("Crop Threshold: " + cropThreshold);
//		print("--------------------------------");
		sliceNumber = "0000" + k;
		kStr = "" + k;
		sliceNumber = substring(sliceNumber,kStr.length);
		selectImage(imageNameBase+"-"+sliceNumber);
		makeRectangle(posX[k-1]-(cropWidth/2), posY[k-1]-(cropHeight*(1-y_centering)), cropWidth, cropHeight);
		run("Crop");
		fixedX = parseInt(posX[k-1]) - cropWidth/2;
		fixedY = parseInt(posY[k-1]) - cropHeight*(1-y_centering);
		cropThreshold = parseInt(posY[k-1]) - 19; // 19 pixels = 2 microns
		substacks = Array.concat(substacks,k);
		cropping_angle_substack = Array.concat(cropping_angle_substack,cropping_angle[k-1]);
	}
	else {
		sliceNumber = "0000" + k;
		kStr = "" + k;
		sliceNumber = substring(sliceNumber,kStr.length);
		selectImage(imageNameBase+"-"+sliceNumber);
		makeRectangle(fixedX, fixedY, cropWidth, cropHeight);
		run("Crop");
//		print("Slice: "+ (k-1));
//		print("Y Position: " + posY[k-1]);
//		print("Crop Threshold: " + cropThreshold);
//		print("--------------------------------");
	}
}

//Add the last frame to the substacks array if not already added.
if(substacks[substacks.length-1] != k-1){
	substacks = Array.concat(substacks,k-1);
	cropping_angle_substack = Array.concat(cropping_angle_substack,cropping_angle[k-1]);
}



//Combine all of the images back to a stack
run("Images to Stack", "name="+imageNameBase+" title="+imageNameBase+" use");

//Split stack to substacks depending on the crop field of view
for(j=1;j<substacks.length;j++){
	selectImage(imageNameBase);
	run("Make Substack...", "slices="+substacks[j-1]+"-"+substacks[j]);
	run("Rotate... ", "angle="+cropping_angle_substack[j-1]+" grid=1 interpolation=Bilinear stack");
}
selectImage(imageNameBase);
close();

showMessageWithCancel("Press OK if you would like to save these videos as an AVI in a folder.");
folder = getDirectory("Select a directory to save your videos.");
for(j=1;j<substacks.length;j++){
	selectImage("Substack ("+substacks[j-1]+"-"+substacks[j]+")");
	run("AVI... ", "compression=JPEG frame=25 save=["+folder+"/"+"Substack ("+substacks[j-1]+"-"+substacks[j]+").avi]");
	close();
}




