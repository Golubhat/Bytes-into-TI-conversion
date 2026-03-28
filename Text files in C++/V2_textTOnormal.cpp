#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main() {
    string outputFile;
    cout << "Enter output binary file name: ";
    getline(cin >> ws, outputFile);

    ofstream output(outputFile, ios::binary);
    if (!output) {
        cerr << "Cannot open output file.\n";
        return 1;
    }

    string charset = "GHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()-_=+[{]};:',<.>/?|";
    size_t base = charset.size();

    int fileIndex = 1;

    while (true) {
        string inputFile = to_string(fileIndex) + ".txt";
        ifstream input(inputFile, ios::binary);
        if (!input) break; // no more files

        char ch;
        while (input.get(ch)) {
            unsigned char byte;
            size_t idx = charset.find(ch);

            if (idx != string::npos) {
                // Single-character mapping
                byte = (unsigned char)idx;
            } else {
                // Hex sequence (two characters)
                char ch2;
                if (!input.get(ch2)) break; // unexpected EOF
                string hex;
                hex += ch;
                hex += ch2;
                byte = (unsigned char)stoi(hex, nullptr, 16);
            }

            output.put(byte);
        }

        input.close();
        fileIndex++;
    }

    output.close();
    cout << "Decoding complete! Output saved as " << outputFile << "\n";
    return 0;
}
