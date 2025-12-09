#!/usr/bin/env python3
"""
AI Model Tracing and Attribution Module
Tracks AI model lineage, datasets, architecture changes, and fine-tuning history
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class DatasetInfo:
    """Information about a training dataset"""
    name: str
    version: str
    source: str
    size: int
    date_collected: str
    license: str
    checksum: str
    metadata: Dict[str, Any]


@dataclass
class ArchitectureChange:
    """Record of an architectural change"""
    timestamp: str
    change_type: str  # "layer_add", "layer_remove", "parameter_change", etc.
    description: str
    parameters_before: int
    parameters_after: int
    changed_by: str
    reason: str


@dataclass
class FineTuningRun:
    """Record of a fine-tuning session"""
    run_id: str
    timestamp: str
    base_model: str
    dataset: str
    hyperparameters: Dict[str, Any]
    metrics: Dict[str, float]
    duration_seconds: float
    final_checkpoint: str


class ModelLineageTracker:
    """Tracks the complete lineage and evolution of AI models"""
    
    def __init__(self, model_id: str, save_dir: str = "model_lineage"):
        self.model_id = model_id
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        self.datasets: List[DatasetInfo] = []
        self.architecture_changes: List[ArchitectureChange] = []
        self.finetuning_runs: List[FineTuningRun] = []
        self.metadata = {
            "model_id": model_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Load existing lineage if available
        self.load_lineage()
    
    def add_dataset(self, dataset_info: DatasetInfo) -> None:
        """Add a dataset to the model's lineage"""
        self.datasets.append(dataset_info)
        self.metadata["last_updated"] = datetime.now().isoformat()
        self.save_lineage()
    
    def add_architecture_change(self, change: ArchitectureChange) -> None:
        """Record an architectural change"""
        self.architecture_changes.append(change)
        self.metadata["last_updated"] = datetime.now().isoformat()
        self.save_lineage()
    
    def add_finetuning_run(self, run: FineTuningRun) -> None:
        """Record a fine-tuning session"""
        self.finetuning_runs.append(run)
        self.metadata["last_updated"] = datetime.now().isoformat()
        self.save_lineage()
    
    def get_lineage_summary(self) -> Dict[str, Any]:
        """Get a summary of the model's lineage"""
        return {
            "model_id": self.model_id,
            "total_datasets": len(self.datasets),
            "total_architecture_changes": len(self.architecture_changes),
            "total_finetuning_runs": len(self.finetuning_runs),
            "created_at": self.metadata.get("created_at"),
            "last_updated": self.metadata.get("last_updated"),
            "datasets": [d.name for d in self.datasets],
            "latest_architecture": self._get_latest_architecture(),
            "best_finetuning_run": self._get_best_finetuning_run()
        }
    
    def _get_latest_architecture(self) -> Dict[str, Any]:
        """Get the current architecture state"""
        if not self.architecture_changes:
            return {"status": "no changes recorded"}
        
        latest = self.architecture_changes[-1]
        return {
            "timestamp": latest.timestamp,
            "parameters": latest.parameters_after,
            "last_change": latest.description
        }
    
    def _get_best_finetuning_run(self) -> Optional[Dict[str, Any]]:
        """Get the best performing fine-tuning run"""
        if not self.finetuning_runs:
            return None
        
        # Assuming higher metrics are better
        best_run = max(
            self.finetuning_runs,
            key=lambda r: sum(r.metrics.values()) / len(r.metrics) if r.metrics else 0
        )
        
        return {
            "run_id": best_run.run_id,
            "timestamp": best_run.timestamp,
            "avg_metric": sum(best_run.metrics.values()) / len(best_run.metrics) if best_run.metrics else 0,
            "metrics": best_run.metrics
        }
    
    def trace_dataset_provenance(self, dataset_name: str) -> Dict[str, Any]:
        """Trace the provenance of a specific dataset"""
        dataset = next((d for d in self.datasets if d.name == dataset_name), None)
        if not dataset:
            return {"error": f"Dataset '{dataset_name}' not found in lineage"}
        
        return {
            "dataset": asdict(dataset),
            "used_in_runs": [
                run.run_id for run in self.finetuning_runs
                if run.dataset == dataset_name
            ]
        }
    
    def get_evolution_timeline(self) -> List[Dict[str, Any]]:
        """Get a chronological timeline of all changes"""
        timeline = []
        
        # Add architecture changes
        for change in self.architecture_changes:
            timeline.append({
                "timestamp": change.timestamp,
                "type": "architecture_change",
                "description": change.description,
                "details": asdict(change)
            })
        
        # Add fine-tuning runs
        for run in self.finetuning_runs:
            timeline.append({
                "timestamp": run.timestamp,
                "type": "finetuning_run",
                "description": f"Fine-tuning on {run.dataset}",
                "details": asdict(run)
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        return timeline
    
    def save_lineage(self) -> None:
        """Save lineage to disk"""
        lineage_file = self.save_dir / f"{self.model_id}_lineage.json"
        
        data = {
            "metadata": self.metadata,
            "datasets": [asdict(d) for d in self.datasets],
            "architecture_changes": [asdict(c) for c in self.architecture_changes],
            "finetuning_runs": [asdict(r) for r in self.finetuning_runs]
        }
        
        with open(lineage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_lineage(self) -> None:
        """Load lineage from disk if it exists"""
        lineage_file = self.save_dir / f"{self.model_id}_lineage.json"
        
        if not lineage_file.exists():
            return
        
        with open(lineage_file, 'r') as f:
            data = json.load(f)
        
        self.metadata = data.get("metadata", self.metadata)
        self.datasets = [DatasetInfo(**d) for d in data.get("datasets", [])]
        self.architecture_changes = [ArchitectureChange(**c) for c in data.get("architecture_changes", [])]
        self.finetuning_runs = [FineTuningRun(**r) for r in data.get("finetuning_runs", [])]
    
    def export_report(self, output_path: str) -> None:
        """Export a comprehensive lineage report"""
        report = {
            "summary": self.get_lineage_summary(),
            "evolution_timeline": self.get_evolution_timeline(),
            "datasets": [asdict(d) for d in self.datasets],
            "architecture_changes": [asdict(c) for c in self.architecture_changes],
            "finetuning_runs": [asdict(r) for r in self.finetuning_runs]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)


def compute_dataset_checksum(data_path: str) -> str:
    """Compute checksum for dataset verification"""
    sha256_hash = hashlib.sha256()
    
    with open(data_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


if __name__ == "__main__":
    # Example usage
    tracker = ModelLineageTracker("kimi-k2-instruct")
    
    # Add a dataset
    dataset = DatasetInfo(
        name="training_dataset_v1",
        version="1.0",
        source="internal",
        size=15500000000000,  # 15.5T tokens
        date_collected="2024-01-01",
        license="Modified MIT",
        checksum="abc123...",
        metadata={"languages": ["en", "zh"], "domains": ["code", "math", "general"]}
    )
    tracker.add_dataset(dataset)
    
    # Add architecture change
    change = ArchitectureChange(
        timestamp=datetime.now().isoformat(),
        change_type="layer_add",
        description="Added shared expert layer",
        parameters_before=980000000000,
        parameters_after=1000000000000,
        changed_by="team",
        reason="Improve task routing"
    )
    tracker.add_architecture_change(change)
    
    # Add fine-tuning run
    run = FineTuningRun(
        run_id="ft_001",
        timestamp=datetime.now().isoformat(),
        base_model="kimi-k2-base",
        dataset="training_dataset_v1",
        hyperparameters={"lr": 1e-5, "batch_size": 32, "epochs": 3},
        metrics={"accuracy": 0.92, "loss": 0.08},
        duration_seconds=172800.0,
        final_checkpoint="checkpoints/ft_001_final.pt"
    )
    tracker.add_finetuning_run(run)
    
    # Get summary
    print(json.dumps(tracker.get_lineage_summary(), indent=2))
    
    # Export report
    tracker.export_report("lineage_report.json")
    print("\n✅ Model lineage tracking example complete!")
