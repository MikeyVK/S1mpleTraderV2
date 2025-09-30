# tests/backend/assembly/test_engine_builder.py
"""
Unit tests for the EngineBuilder class.
"""
from unittest.mock import call
from pytest_mock import MockerFixture

from backend.assembly.engine_builder import EngineBuilder
from backend.assembly.worker_builder import WorkerBuilder
from backend.config.schemas.run_schema import RunBlueprint, WorkerDefinition
from backend.core.enums import PipelinePhase

def test_build_context_pipeline(mocker: MockerFixture):
    """
    Tests if the context pipeline is built correctly by only requesting
    workers from the STRUCTURAL_CONTEXT phase.
    """
    # --- Arrange ---
    mock_worker_builder = mocker.MagicMock(spec=WorkerBuilder)
    mock_run_conf = mocker.MagicMock(spec=RunBlueprint)

    # --- DE FIX: Maak de geneste mock-structuur voor de taskboard ---
    mock_taskboard = mocker.MagicMock()
    mock_taskboard.root = {
        PipelinePhase.STRUCTURAL_CONTEXT: ["worker_a", "worker_b"],
        PipelinePhase.SIGNAL_GENERATOR: ["worker_c"]  # Should be ignored
    }
    mock_run_conf.taskboard = mock_taskboard
    # ----------------------------------------------------------------

    # --- DE FIX: Mock ook de workforce met een get methode ---
    mock_workforce = mocker.MagicMock()
    mock_workforce.get.return_value = WorkerDefinition()
    mock_run_conf.workforce = mock_workforce
    # ---------------------------------------------------------

    # --- Act ---
    builder = EngineBuilder(worker_builder=mock_worker_builder)
    builder.build_context_pipeline(run_conf=mock_run_conf)

    # --- Assert ---
    # Verify that 'build' was called only for the context workers
    expected_calls = [
        call(name="worker_a", user_params={}),
        call(name="worker_b", user_params={})
    ]
    mock_worker_builder.build.assert_has_calls(expected_calls, any_order=True)
    assert mock_worker_builder.build.call_count == 2

def test_build_engine(mocker: MockerFixture):
    """
    Tests if the StrategyEngine is assembled correctly with workers from all
    phases EXCEPT the STRUCTURAL_CONTEXT phase.
    """
    # --- Arrange ---
    mock_worker_builder = mocker.MagicMock(spec=WorkerBuilder)
    mock_strategy_engine_class = mocker.patch('backend.assembly.engine_builder.StrategyEngine')
    mock_run_conf = mocker.MagicMock(spec=RunBlueprint)

    # --- DE FIX: Maak de geneste mock-structuur voor de taskboard ---
    mock_taskboard = mocker.MagicMock()
    mock_taskboard.root = {
        PipelinePhase.STRUCTURAL_CONTEXT: ["context_worker"],  # Should be ignored
        PipelinePhase.SIGNAL_GENERATOR: ["signal_worker_1"],
        PipelinePhase.SIGNAL_REFINER: ["refiner_worker_1", "refiner_worker_2"]
    }
    mock_run_conf.taskboard = mock_taskboard
    # ----------------------------------------------------------------

    # --- DE FIX: Mock ook de workforce met een get methode ---
    mock_workforce = mocker.MagicMock()
    mock_workforce.get.return_value = WorkerDefinition()
    mock_run_conf.workforce = mock_workforce
    # ---------------------------------------------------------

    # --- Act ---
    builder = EngineBuilder(worker_builder=mock_worker_builder)
    builder.build_engine(run_conf=mock_run_conf)

    # --- Assert ---
    # Verify the worker_builder was called for the correct, non-context workers
    expected_build_calls = [
        call(name="signal_worker_1", user_params={}),
        call(name="refiner_worker_1", user_params={}),
        call(name="refiner_worker_2", user_params={})
    ]
    mock_worker_builder.build.assert_has_calls(expected_build_calls, any_order=True)
    assert mock_worker_builder.build.call_count == 3

    # Verify the StrategyEngine was instantiated with the correctly grouped workers
    active_workers_arg = mock_strategy_engine_class.call_args[1]['active_workers']

    assert PipelinePhase.SIGNAL_GENERATOR.value in active_workers_arg
    assert len(active_workers_arg[PipelinePhase.SIGNAL_GENERATOR.value]) == 1

    assert PipelinePhase.SIGNAL_REFINER.value in active_workers_arg
    assert len(active_workers_arg[PipelinePhase.SIGNAL_REFINER.value]) == 2

    # Crucially, assert that the context phase was NOT included in the engine's workers
    assert PipelinePhase.STRUCTURAL_CONTEXT.value not in active_workers_arg
