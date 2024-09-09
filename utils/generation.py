from utils.get_index import * 


index = create_index()

def final_result(query):
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return response, query

def format_output(answer, query):
    # Main answer response
    response_block = f"{answer.response}\n\n"

    # Source information block
    source_block = ""
    if answer.source_nodes:
        source_block += "You can read more of it at: \n"
        for node in answer.source_nodes:
            # Extracting metadata
            metadata = node.node.metadata
            page = metadata.get('page_label', 'N/A')
            source = metadata.get('file_name', 'N/A')

            # Formatting the source information
            source_block += f"- Page {page} from {source}\n"
        source_block += "\n"
    
    return response_block, source_block