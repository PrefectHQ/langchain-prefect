from langchain.llms import OpenAI

from langchain_prefect.utilities import NotAnArtifact, llm_invocation_summary


class TestParseInvocationSummary:
    def test_parse_callable_llm(self):
        """Test that LLM invocation summary is parsed correctly using a callable LLM."""
        llm_input = "What would be a good name for a company that makes colorful socks?"

        artifact = llm_invocation_summary(
            OpenAI(), llm_input, invocation_fn=lambda x: None
        )

        assert isinstance(artifact, NotAnArtifact)

        assert artifact.content["llm_endpoint"] == "langchain.llms.openai"
        assert artifact.content["prompts"] == llm_input
