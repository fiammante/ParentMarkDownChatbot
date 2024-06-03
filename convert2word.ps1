# Create a new Word.Application object
$word = New-Object -ComObject Word.Application

# Don't display the Word application on screen
$word.Visible = $false

# Define the folder path (replace 'C:\your\folder\path' with your actual path)
$folderPath = "D:\data\pdf"

# Get all PDF files in the folder
$pdfFiles = Get-ChildItem -Path $folderPath -Filter *.pdf

# Loop through each PDF file
foreach ($documentPath in $pdfFiles) {
	Write-Host "Processing file: $documentPath"
	# Extract the path without extension
	$filePathWithoutExt = $documentPath.FullName.Substring(0, $documentPath.FullName.LastIndexOf('.'))

	# Create the new HTML file path (append .html extension)
	$pdfFolder = "pdf"
	$docFolder = "word"
	$markdownFolder = "md"
	$attachmentFolder = "md\attachments"
	
	# Replace the subfolder name in the path
	$docPath = $filePathWithoutExt.Replace($pdfFolder, $docFolder) + ".docx"
	$markdownPath = $filePathWithoutExt.Replace($pdfFolder, $markdownFolder) + ".md"
	$attachmentsPath = $filePathWithoutExt.Replace($pdfFolder, $attachmentFolder)
	# **Note:** You'll need to add logic to create the HTML content here
	# (e.g., convert from PDF text or create new HTML content)

	$document = $word.Documents.Open($($documentPath.FullName))
	# Write-Host message (optional)
	Write-Host "Created Doc file: $docPath"
	# Save the document as Doc
	$wdFormatDocumentDefault = 16  # Word default document format
	$document.SaveAs([Ref] $docPath, [Ref] $wdFormatDocumentDefault)
	# Define the pandoc command
	$pandocCommand = "pandoc -t markdown_strict+grid_tables --wrap=none --columns=200 --extract-media=`"$attachmentPath`" `"$docPath`" -o `"$markdownPath`"  "
	Write-Host  $pandocCommand	
	Write-Host "Created Markdown file: $markdownPath"
	# Call the pandoc command
	Invoke-Expression $pandocCommand

	# $document.Close()

}


# Quit Word application
$word.Quit()
# Clean up the COM objects
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($document) | Out-Null

# Clean up the COM objects
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
