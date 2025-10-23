"""
timer.py - Utility untuk mengukur waktu eksekusi algoritma

Menyediakan context manager untuk pengukuran waktu yang mudah dan akurat.
"""

import time
from typing import Optional

class Timer:
    """
    Context manager untuk mengukur waktu eksekusi.
    
    Usage:
        with Timer() as t:
            # kode yang ingin diukur
            algorithm.solve()
        
        print(f"Duration: {t.duration:.4f} seconds")
    """
    
    def __init__(self, name: Optional[str] = None, verbose: bool = False):
        """
        Args:
            name: Nama timer (untuk identifikasi)
            verbose: Jika True, akan print durasi otomatis
        """
        self.name = name
        self.verbose = verbose
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        """Start timer saat masuk context"""
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer saat keluar context"""
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        
        if self.verbose:
            name_str = f"[{self.name}] " if self.name else ""
            print(f"{name_str}Duration: {self.duration:.4f} seconds")
        
        return False  # Don't suppress exceptions
    
    def get_duration_ms(self) -> float:
        """Return durasi dalam milliseconds"""
        return self.duration * 1000 if self.duration else 0.0
    
    def get_duration_str(self) -> str:
        """Return durasi dalam format string yang readable"""
        if self.duration is None:
            return "N/A"
        
        if self.duration < 0.001:
            return f"{self.duration * 1000000:.2f} μs"
        elif self.duration < 1.0:
            return f"{self.duration * 1000:.2f} ms"
        elif self.duration < 60:
            return f"{self.duration:.2f} s"
        else:
            minutes = int(self.duration // 60)
            seconds = self.duration % 60
            return f"{minutes}m {seconds:.2f}s"


class PerformanceMonitor:
    """
    Class untuk monitoring performa algoritma dengan lebih detail.
    Berguna untuk eksperimen dan analisis.
    """
    
    def __init__(self):
        self.metrics = {}
        self.timers = {}
    
    def start_timer(self, name: str):
        """Mulai timer untuk operasi tertentu"""
        self.timers[name] = time.perf_counter()
    
    def stop_timer(self, name: str) -> float:
        """Stop timer dan return duration"""
        if name not in self.timers:
            raise ValueError(f"Timer '{name}' belum di-start")
        
        duration = time.perf_counter() - self.timers[name]
        
        # Simpan ke metrics
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(duration)
        
        return duration
    
    def get_average(self, name: str) -> float:
        """Get rata-rata durasi untuk operasi tertentu"""
        if name not in self.metrics or len(self.metrics[name]) == 0:
            return 0.0
        return sum(self.metrics[name]) / len(self.metrics[name])
    
    def get_total(self, name: str) -> float:
        """Get total durasi untuk operasi tertentu"""
        if name not in self.metrics:
            return 0.0
        return sum(self.metrics[name])
    
    def get_count(self, name: str) -> int:
        """Get berapa kali operasi tertentu dipanggil"""
        if name not in self.metrics:
            return 0
        return len(self.metrics[name])
    
    def summary(self) -> dict:
        """Return summary dari semua metrics"""
        return {
            name: {
                "count": self.get_count(name),
                "total": self.get_total(name),
                "average": self.get_average(name),
                "min": min(times) if times else 0.0,
                "max": max(times) if times else 0.0
            }
            for name, times in self.metrics.items()
        }
    
    def print_summary(self):
        """Print summary dalam format yang readable"""
        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)
        
        summary = self.summary()
        for name, stats in summary.items():
            print(f"\n{name}:")
            print(f"  Count   : {stats['count']}")
            print(f"  Total   : {stats['total']:.4f}s")
            print(f"  Average : {stats['average']:.4f}s")
            print(f"  Min     : {stats['min']:.4f}s")
            print(f"  Max     : {stats['max']:.4f}s")
    
    def reset(self):
        """Reset semua metrics"""
        self.metrics = {}
        self.timers = {}


# Demo penggunaan
def demo_timer():
    """Demo penggunaan Timer dan PerformanceMonitor"""
    import random
    
    print("Demo Timer - Simple Usage")
    print("-" * 40)
    
    # Simple timer
    with Timer(name="Example Operation", verbose=True) as t:
        # Simulasi operasi
        time.sleep(0.1)
    
    print(f"Duration: {t.get_duration_str()}\n")
    
    # Performance Monitor
    print("Demo PerformanceMonitor - Multiple Operations")
    print("-" * 40)
    
    monitor = PerformanceMonitor()
    
    # Simulasi multiple operations
    for i in range(5):
        monitor.start_timer("operation_A")
        time.sleep(random.uniform(0.01, 0.05))
        monitor.stop_timer("operation_A")
        
        monitor.start_timer("operation_B")
        time.sleep(random.uniform(0.02, 0.08))
        monitor.stop_timer("operation_B")
    
    monitor.print_summary()


if __name__ == "__main__":
    demo_timer()