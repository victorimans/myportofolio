Nama : Victoriano Iman Santosa

NPM : 2506544353

Kelas : PBP B

## AI disclosure

Saya menggunakan ChatGPT Plus sebagai alat bantu selama pengembangan, terutama karena pemahaman saya terhadap CSS belum mendalam. Saya memberikan spesifikasi visual, batasan proyek, struktur section, dan constraint yang harus dipertahankan lalu AI kemudian membantu menghasilkan atau menjelaskan sebagian styling dan solusi frontend.

AI tidak menjadi sumber kebenaran final. Beberapa keterbatasannya adalah:

- AI dapat menghasilkan CSS yang valid secara sintaks tetapi tidak sesuai dengan maksud visual atau struktur halaman;
- AI dapat menyarankan property, breakpoint, atau abstraksi yang tidak perlu;
- AI tidak otomatis mengetahui apakah sebuah klaim portfolio benar-benar didukung oleh pengalaman saya;
- AI tidak dapat menggantikan pemeriksaan nyata pada browser, perangkat berbeda, keyboard navigation, reduced-motion preference, maupun environment Django;
- jawaban AI dapat terdengar meyakinkan meskipun belum diuji pada repository yang sebenarnya.

Perbaikan dan validasi manual yang saya lakukan meliputi:

- Menetapkan spesifikasi dan constraint sebelum meminta bantuan AI;
- Mereview output AI terhadap struktur dan kebutuhan portfolio;
- Memeriksa hasil visual pada beberapa ukuran viewport dan perangkat;
- Mempertahankan hanya konten yang dapat dipertanggungjawabkan, termasuk penggunaan coming-soon untuk Projects dan Journey;
- Membedakan hasil manual visual review dari automated verification yang belum boleh diklaim berhasil tanpa bukti.

Dengan demikian, AI digunakan sebagai alat bantu eksplorasi dan produksi awal, sedangkan keputusan akhir, batas klaim, review hasil, dan tanggung jawab terhadap repository tetap berada pada saya.

## Referensi percakapan AI

Semua percakapan AI yang berkaitan dengan proyek ini dapat dicantumkan di bagian berikut setelah tersedia dalam bentuk URL share:

- Percakapan AI - perencanaan dan penyusunan portfolio: `https://chatgpt.com/s/cx_6a9edfaedb388191b4e2ea65177ceb57`
- Percakapan AI - review desain dan dokumentasi: `https://chatgpt.com/s/cx_6a9edfdb5c3c8191802238e9ddc543ff`
- Percakapan AI - bantuan CSS, responsive layout, dan accessibility: `https://chatgpt.com/s/cx_6a9edff9daa081918a1dc80568ca1c4c`

Placeholder di atas sengaja tidak diganti dengan URL buatan. Tautan percakapan harus berasal dari URL share ChatGPT yang benar-benar dibuat oleh pemilik percakapan.

## Kontribusi

Saran perbaikan dapat diajukan melalui issue atau pull request. Perubahan sebaiknya:

1. Menjelaskan masalah atau tujuan perubahan;
2. Menjaga konten portfolio tetap truthful;
3. Mempertahankan responsiveness dan visible focus state;
4. Menyertakan cara verifikasi yang dilakukan; dan
5. Tidak menambah dependency atau kompleksitas tanpa kebutuhan yang jelas.

## Notes :
Adapun AGENTS.md, CONTEXT.md, dan docs folders. Berisi mengenai hal hal yang saya persiapkan dan memantain supaya pada saat AI mengerjakan terjadi minim AI hallucination karena AI memiliki konteks yang jelas.


## Tugas 1

# Soal :
1. Pada Tutorial dan Tugas 1, Anda diberi kebebasan untuk menentukan tampilan dari website portofolio Anda. Saat Anda merancang struktur HTML yang digunakan, apakah Anda menggunakan elemen semantik HTML5 seperti <section>, <article>, atau <aside>? Jika iya, bagaimana elemen tersebut membantu Anda dalam membuat static web? Jika tidak, mengapa tanpa elemen tersebut sudah memenuhi kebutuhan desain Anda?

2. Ketika Anda mengatur CSS Anda agar tetap responsive, tantangan tata letak apa yang Anda temukan? Bagaimana Anda mengevaluasi elemen mana yang harus diubah posisinya atau diprioritaskan ukurannya saat berpindah dari tampilan desktop ke mobile?

3. Website yang Anda buat saat ini adalah static web murni. Batasan apa yang Anda rasakan saat mencoba menyajikan informasi pada portofolio Anda secara optimal? Berdasarkan batasan tersebut, fungsionalitas dinamis apa yang paling ingin Anda persiapkan dan tambahkan pada iterasi proyek selanjutnya?

# Jawaban :
1. Saya menggunakan elemen semantik HTML5 seperti <header>, <nav>, <main>, <section>, dan <footer> untuk menggambarkan fungsi dari setiap bagian website. Misalnya, <section> digunakan untuk memisahkan bagian About, Skills, Projects, dan Contact, sedangkan <nav> digunakan untuk bagian navigasi. Menurut pendapat saya, elemen semantik membantu membuat struktur HTML menjadi lebih jelas, terorganisasi, dan mudah dipahami oleh developer. Elemen ini juga meningkatkan aksesibilitas karena screen reader dapat mengenali fungsi setiap bagian halaman. Meskipun website yang dibuat bersifat statis, elemen semantik tetap penting untuk menjaga keteraturan dan memudahkan pemeliharaan kode. Static web juga tidak selalu berarti seluruh website harus berada dalam satu file, melainkan kontennya tidak dihasilkan secara dinamis dari database atau server.

2. Tantangan utama yang saya temukan adalah menyesuaikan tata letak website dari ukuran desktop ke mobile. Beberapa elemen seperti navigasi, teks, gambar, tombol, dan kartu proyek dapat terlihat terlalu besar, bertumpuk, atau keluar dari layar ketika ditampilkan pada perangkat dengan ukuran lebih kecil. Untuk mengatasinya, saya perlu menentukan prioritas informasi. Informasi utama seperti nama, deskripsi singkat, dan tombol penting harus tetap terlihat lebih dahulu pada tampilan mobile. Saya menggunakan CSS seperti flexbox, grid, media queries, rem, dan vw agar ukuran elemen dapat menyesuaikan layar. Saya juga mengevaluasi hasilnya menggunakan browser pada berbagai ukuran layar dan memeriksa apakah teks tetap terbaca, tombol mudah ditekan, serta tidak terjadi horizontal scrolling.

3. Karena website saya masih berupa static web, informasi di dalamnya harus diperbarui secara manual melalui kode HTML. Hal ini menjadi keterbatasan ketika saya ingin menambahkan proyek baru, memperbarui informasi, atau mengelola banyak konten. Selain itu, fitur seperti pencarian, penyaringan proyek, formulir kontak, login, dan penyimpanan data belum dapat dilakukan secara optimal tanpa bantuan backend atau database.