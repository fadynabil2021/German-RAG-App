import pytest
from unittest.mock import AsyncMock, MagicMock
from domains.tutor.service import TutorService
from domains.tutor.interfaces import TutoringMode

@pytest.mark.asyncio
async def test_tutor_response_socratic():
    # Mock LLM Provider
    llm_provider = AsyncMock()
    llm_provider.generate_text.return_value = "Was denkst du darüber?"
    llm_provider.process_text = MagicMock(side_effect=lambda x: x)
    llm_provider.construct_prompt = MagicMock(side_effect=lambda prompt, role: {"role": role, "content": prompt})
    llm_provider.enums = MagicMock()
    llm_provider.enums.SYSTEM.value = "system"
    llm_provider.enums.USER.value = "user"
    
    # Mock Template Parser
    template_parser = MagicMock()
    template_parser.get.return_value = "Mock template content"
    
    # Instantiate Service
    service = TutorService(
        llm_provider=llm_provider,
        vectordb_client=AsyncMock(),
        embedding_client=AsyncMock(),
        template_parser=template_parser
    )
    
    # Call method
    response = await service.tutor_response(
        query="Wie geht es dir?",
        context=["Ich bin ein Dokument."],
        level="A1",
        mode=TutoringMode.SOCRATIC
    )
    
    # Assertions
    assert response == "Was denkst du darüber?"
    llm_provider.generate_text.assert_called_once()

@pytest.mark.asyncio
async def test_retrieve_context():
    # Mock Embedding Client
    embedding_client = AsyncMock()
    embedding_client.embed_text.return_value = [0.1, 0.2, 0.3]
    
    # Mock Vector DB Client
    vectordb_client = AsyncMock()
    mock_result = MagicMock()
    mock_result.text = "Gefundener Text"
    mock_result.score = 0.9
    mock_result.metadata = {"page": 1}
    vectordb_client.search_by_vector.return_value = [mock_result]
    vectordb_client.default_vector_size = 1536
    
    # Instantiate Service
    service = TutorService(
        llm_provider=AsyncMock(),
        vectordb_client=vectordb_client,
        embedding_client=embedding_client,
        template_parser=MagicMock()
    )
    
    # Call method
    results = await service.retrieve_context(
        query="Suche nach etwas",
        project_id=1,
        limit=1
    )
    
    # Assertions
    assert len(results) == 1
    assert results[0]["text"] == "Gefundener Text"
    assert results[0]["score"] == 0.9
    embedding_client.embed_text.assert_called_once()
    vectordb_client.search_by_vector.assert_called_once()
