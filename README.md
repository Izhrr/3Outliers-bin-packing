# 3Outliers Bin Packing

<div align="center">
  <br>
  <img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/c39265b1-a855-476a-a195-9396ae330b89" />
</div>

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

## Pembagian Tugas Anggota Kelompok

| NIM       | Nama                         | Kontribusi                                                                                                         |
|-----------|------------------------------|--------------------------------------------------------------------------------------------------------------------|
| 18223120  | Leonard Arif Sutiono         | Membuat README, Mengimplementasikan kode untuk algoritma Genetic Algorithm, Mendesain tampilan visual output state pada CLI, Mengintegrasikan data hasil output pada setiap algoritma ke main, Mengerjakan laporan bagian hasil dan pembahasan untuk Genetic Algorithm, saran, dan kesimpulan |
| 18223129  | Izhar Alif Akbar             | Inisialisasi struktur kode, Membuat pipeline untuk integrasi keseluruhan kode, Mengimplementasikan kode untuk algoritma Simulated Annealing, Membantu mengimplementasikan kode untuk algoritma Hill-Climbing, Mendefinisikan objective function, Mengerjakan laporan bagian pendahuluan, hasil dan pembahasan untuk Simulated Annealing, kesimpulan, dan saran |
| 18223136  | Geraldo Linggom Samuel T.    | Mengimplementasikan kode untuk algoritma Hill Climbing, Mengerjakan laporan bagian pendahuluan, hasil dan pembahasan untuk Hill Climbing, kesimpulan, dan saran |

## Kontribusi & Kembangkan
- Fork repo ini dan buat branch untuk fitur/algoritma baru.
- Pull request sangat diapresiasi!
- Silakan laporkan bug atau ide pengembangan melalui Issues.

## Lisensi
MIT License
