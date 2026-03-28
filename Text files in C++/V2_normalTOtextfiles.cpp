#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main() {
    string inputFile;
    cout << "Enter input file name: ";
    getline(cin >> ws, inputFile);

    ifstream input(inputFile, ios::binary);
    if (!input) {
        cerr << "Cannot open input file.\n";
        return 1;
    }

    string charset = "GHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()-_=+[{]};:',<.>/?|";
    size_t base = charset.size();
    long long maxFileSize = 1073741822;

    int fileIndex = 1;
    ofstream output(to_string(fileIndex) + ".txt", ios::binary);
    long long currentSize = 0;

    unsigned char byte;
    while (input.read((char*)&byte, 1)) {
        string code;

        if (byte < base) {
            // Single-character encoding
            code += charset[byte];
        } else {
            // Two-character hex encoding
            char buf[3];
            sprintf(buf, "%02X", byte);
            code = buf;
        }

        // Check file size
        if (currentSize + code.size() > maxFileSize) {
            output.close();
            fileIndex++;
            output.open(to_string(fileIndex) + ".txt", ios::binary);
            currentSize = 0;
        }

        output.write(code.c_str(), code.size());
        currentSize += code.size();
    }

    output.close();
    input.close();
    cout << "Encoding complete! Files written sequentially.\n";
    return 0;
}
