# Azure RAG and Debug Session Worklog

This document records the Azure RAG notebook setup, errors encountered, fixes applied, and the Debug Session verification performed for this project.

## What was built and verified

- Corrected the local Azure AI Search endpoint to the `silver-docs-search` service. The endpoint is stored in the ignored local `.env` file and is intentionally not copied here.
- Created the `airbnb-rag-v1` index for the hybrid RAG notebook with `id`, `content`, `content_vector`, and `metadata` fields. The vector field uses 1,536 dimensions to match the configured embedding deployment.
- Added PDF ingestion to `azure_ai_search_hybrid_rag.ipynb` and added `pypdf>=5.0` to `requirements.txt`.
- Indexed 43 listings from the Airbnb PDF. Notebook validation confirmed 43 searchable documents with 43 unique IDs, hybrid retrieval results, and generated answers with citations.
- Updated notebook dotenv loading to `load_dotenv(override=True)` so an old environment value cannot silently override the endpoint in `.env`.
- Confirmed the notebook's direct-upload index (`airbnb-rag-v1`) is separate from the skillset/indexer pipeline for `silver-docs`. The direct-upload index does not contain a `language` field.

The notebook expects the source PDF at `downloads/adbf1dfa3b5b_airbnb_listings.pdf`. The `downloads/` directory is ignored by Git; provide the PDF locally before running the ingestion cell.

## Errors and resolutions

### 1. Search endpoint did not resolve

**Observed:** The notebook initially used `https://aisearchm.search.windows.net`, which failed DNS resolution.

**Resolution:** Updated the local `.env` endpoint to the existing Search service endpoint for `silver-docs-search`. The corrected value is not recorded here because environment-specific configuration belongs in `.env`, not source control.

### 2. Notebook index did not exist

**Observed:** The configured `airbnb-rag-v1` index was absent. The existing `silver-docs` index had a different schema and did not provide the notebook's required `id`, `content`, and `content_vector` fields.

**Resolution:** Created a separate `airbnb-rag-v1` index with the fields the notebook uses and the embedding model's 1,536-dimensional vector size.

### 3. New index contained no documents

**Observed:** The index was created successfully but initially had zero documents.

**Resolution:** Added a PDF ingestion step to the notebook. It parses the Airbnb PDF into 43 listings, creates embeddings, and uploads with `merge_or_upload_documents` so rerunning ingestion is idempotent for matching IDs. The subsequent notebook run indexed all 43 listings and verified their retrieval.

### 4. Stale endpoint remained in the notebook process

**Observed:** A notebook cell showed an old endpoint even after `.env` had been corrected. An already-set process environment variable can take precedence over dotenv values.

**Resolution:** Changed dotenv loading to `load_dotenv(override=True)`. The configuration cell then connected to the expected Search service and reported the 43 indexed documents.

### 5. Debug Session could not read or write execution data

**Observed:** The `firstdebug` session showed storage authorization errors, including inability to persist events and retrieve execution data. The local Blob connection could access the storage account, so local connectivity alone did not prove the Debug Session's stored authentication was valid.

**Resolution:** Granted the `silver-docs-search` system-assigned managed identity the `Storage Blob Data Contributor` role on the `corpordrage` storage account. A replacement session, `firstdebug-fixed`, was created using that account and managed identity. Its run completed and returned enriched data.

**Azure-side change:** The role assignment is in Azure RBAC and is not created by this Git repository. Review it in Azure before applying this setup to another environment.

### 6. A debug run selected a manifest instead of the desired document

**Observed:** The first successful run of `firstdebug-fixed` selected `_complete.json`. Its content was a small JSON manifest, not the Markdown chunk being investigated.

**Resolution:** Created a session with **Debug specific document** and supplied the exact Blob URL for `chunk_0001.md` in the `silver` container.

### 7. Wrong Markdown filename and debug-session quota

**Observed:** An initial attempt used `chunk.md`, which was not the actual blob name. The run did not produce execution data. Creating a new session also hit the service limit of three debug sessions.

**Resolution:** After the user supplied the actual URL ending in `chunk_0001.md`, deleted the old `firstdebug` session with the user's approval to free a quota slot. The unsuccessful temporary `chunk-md-debug` session was also deleted rather than left consuming a slot.

**Current sessions at last verification:** `chunk-0001-md-debug`, `firstdebug-fixed`, and `test`. The service had a maximum of three sessions at the time, so remove an unused session before creating another one if that limit still applies.

## Final Debug Session result

The `chunk-0001-md-debug` session ran against:

`https://corpordrage.blob.core.windows.net/silver/x-be797b9c58ba/3cdb10932257/chunk_0001.md`

Azure Portal reported the run as **Completed**. The enriched document confirmed:

- `metadata_storage_name`: `chunk_0001.md`
- `language`: `en` (English), with language detection confidence `1.0`
- `content`: begins with text identifying Databricks Academy and Prakhar Srivastava

The observed file size in the enriched data was 302 bytes.

## Portal display issue

When expanding the content in Azure Portal, the browser logged a CORS failure for a Search Debug Session document-structure request. This did not prevent the completed run or the enriched fields from being displayed; it affected that Portal content-preview interaction.

## Current skillset pipeline and options

The existing `silver-docs-skillset` applies Language Detection to `/document/content`, writes `/document/language`, then passes the text and language into Split. The split output is projected into the `silver-docs` index together with title and storage path.

Additional built-in or connected skills can be added when needed, for example OCR for scanned pages, key phrase extraction, entity recognition, PII detection, translation, sentiment, Azure OpenAI embeddings, or custom Web API processing. Choose skills based on the desired indexed fields and retrieval behavior; some require separate Azure services and can add cost.

The actual Azure skillset configuration is managed in the Azure Search service. This repository documents the observed pipeline but does not deploy or update that Azure resource.

## Safe setup and rerun notes

1. Copy `.env.example` to `.env` and fill in the Azure endpoint, deployment, index, and credential values locally. Never commit `.env` or paste secret values into this document.
2. Install dependencies with `pip install -r requirements.txt`.
3. Place the Airbnb PDF at `downloads/adbf1dfa3b5b_airbnb_listings.pdf`.
4. Run all cells in `azure_ai_search_hybrid_rag.ipynb`. Check the reported document count and a hybrid-search result before relying on generated answers.
5. For Azure Search Debug Sessions, select the correct indexer, storage account, and specific Blob URL. Authenticate with managed identity where configured, and check the service's session quota before creating another session.

For official skill definitions, see [Azure AI Search built-in skills](https://learn.microsoft.com/azure/search/cognitive-search-predefined-skills).
