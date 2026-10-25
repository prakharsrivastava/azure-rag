# Azure RAG demo

## Architecture

Azure Blob Storage (PDFs) -> Azure AI Document Intelligence (`prebuilt-layout`, Markdown) -> Markdown Header Text Splitter -> Azure OpenAI Embeddings -> Azure AI Search (`test`) -> GPT chat model.

## Azure Portal setup

1. Create a resource group, e.g. `rg-langchain-rag-dev`.
2. Create a **Storage account** (Standard LRS), then a **private Blob container** named `test`; upload PDFs. Under Storage account > Access keys copy a connection string (or use `az login` and Storage Blob Data Reader permissions).
3. Create **Azure AI Document Intelligence**. Under Keys and Endpoint, copy the endpoint and key.
4. Create **Azure AI Search**. Under Overview copy the service URL; under Settings > Keys copy an admin key. The Python vector store creates index `test` on first initialization when permitted.
5. Create **Azure OpenAI** (or an Azure OpenAI resource via Microsoft Foundry). In Foundry, deploy a chat model (example deployment name `gpt-4o-mini`) and embedding model (example `text-embedding-ada-002`), subject to regional availability and quotas. Copy the resource endpoint and key under Keys and Endpoint. Use the *deployment names*, not just model names, in `.env`.
6. Copy `.env.example` to `.env` and fill in the actual settings. Do not commit `.env`.

## Run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env       # Windows: copy .env.example .env
python azure_rag.py
```

## Class and methods

- `AzureRAG.__init__`: initialize credentials, Blob client, embedding client, vector store and chat model.
- `AzureRAG.download_blobs`: list and download PDFs from container.
- `AzureRAG.process_document`: layout extraction, Markdown section splitting, size-based chunking and metadata.
- `AzureRAG.ingest_documents`: embed and index chunks.
- `AzureRAG.ask`: retrieve top three chunks and answer with sources.

## Notes

- This is a learning demo, **not production incremental indexing**: re-running ingestion creates duplicates. Implement stable IDs and upserts/deletions before production.
- The API version and deployment names must be supported by your Azure OpenAI resource.
- `azure-cosmos` is installed for future expansion, but not used by this initial demo.
- Do not disable SSL verification. Never share `.env` keys.
- Azure resources may incur costs even if you have a trial account.
