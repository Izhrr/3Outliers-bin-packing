<img width="252" height="200" alt="image" src="https://github.com/user-attachments/assets/c3cb49a3-3c14-44ec-9202-355857b5affa" />
# 3Outliers Bin Packing

## Deskripsi
**3Outliers Bin Packing** adalah proyek Python yang mengimplementasikan berbagai algoritma _local search_ dan _metaheuristics_ untuk menyelesaikan masalah **Bin Packing Problem** (BPP). Proyek ini mendemonstrasikan dan membandingkan efektivitas beberapa algoritma pencarian seperti Hill Climbing (dengan berbagai varian), Genetic Algorithm, dan Simulated Annealing pada kasus pengemasan barang ke dalam container dengan kapasitas terbatas.

## Fitur Utama
- Implementasi berbagai algoritma local search (Steepest Ascent, Stochastic, Sideways Move, Random Restart Hill Climbing)
- Implementasi Genetic Algorithm dengan crossover, mutasi, dan inisialisasi populasi beragam
- Implementasi Simulated Annealing
- Perbandingan performa tiap algoritma (jumlah container, waktu eksekusi, dsb)
- Visualisasi hasil dalam bentuk ASCII (langsung di terminal)
- Export hasil ke file CSV/JSON untuk analisis lebih lanjut
- Modular dan mudah dikembangkan untuk eksperimen algoritma lainnya

## Struktur Direktori
```
├── data/               # Data input (format JSON)
│   └── input/
├── src/                # Kode sumber utama
│   ├── algorithms/     # Implementasi algoritma (GA, Hill Climbing, dsb)
│   ├── core/           # Struktur state, objective function, dan inisialisasi
│   ├── utils/          # Utility: visualizer, file handler, timer, dll
│   └── main.py         # Entry point utama
├── output/             # Hasil eksperimen (CSV/JSON)
├── README.md
└── requirements.txt
```

## Cara Menjalankan

### 1. Persiapan Lingkungan
Pastikan Python 3.7+ sudah terinstall.  
Install dependensi:
```bash
pip install -r requirements.txt
```
*(Jika tidak ada requirements.txt, proyek ini umumnya hanya membutuhkan Python standar)*

### 2. Menjalankan Program
Jalankan program utama dengan input file:
```bash
python src/main.py --input <file directory>
```
Opsi lain:
- `--demo` : Menjalankan demo otomatis dengan data acak.
- `--algorithm [all|steepest|stochastic|sideways|sa|ga]` : Pilih algoritma yang ingin dijalankan.

### 3. Output
- Hasil visualisasi akan muncul di terminal (ASCII art dan ringkasan tabel).
- Hasil eksperimen akan disimpan ke folder `/output` dalam format CSV/JSON.

## Format Input
Input berupa file JSON dengan format:
```json
{
  "capacity": 100,
  "items": {
    "BRG001": 40,
    "BRG002": 55,
    ...
  }
}
```

## Kontribusi & Kembangkan
- Fork repo ini dan buat branch untuk fitur/algoritma baru.
- Pull request sangat diapresiasi!
- Silakan laporkan bug atau ide pengembangan melalui Issues.

## Lisensi
MIT License

