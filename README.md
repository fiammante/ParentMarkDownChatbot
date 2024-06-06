# ParentMarkDownChatbot
A local LLM+RAG chatbot with structured pdf ingestion using Word to convert pdf to docx, and then pandoc to convert from docx to markdown enabling the use of langchain ParentDocumentRetriever with MarkdownTextSplitter.

Uses Powershell with MS Word to open pdf file and convert to docx format, an impressive converter that finds and converts tables, then converts with pandoc to Markdown format.
ParentDocumentRetriever uses a chain of splitters to avoid having too small chunks retrieved in the context.

Replace the paths in the powershell script and notebook by your path.
The script should be executed first to create the markdown files from pdfs

Once the Chroma and VectorStore are loaded with documents the streamlit chatbotparentchild.py can be used by using the command "streamlit run chatbotparentchild.py"
![image](files:chatbotscreenshot.png)
