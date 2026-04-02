#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main()
{
    string charset;
    for (int i = 35; i <= 126; i++) // 92 characters
        charset += char(i);

    string fileName;
    cout << "Enter input file name: ";
    getline(cin >> ws, fileName);

    ifstream input(fileName, ios::binary);
    if (!input)
    {
        cout << "Error opening input file.\n";
        return 1;
    }

    int fileIndex = 1;
    ofstream output(to_string(fileIndex) + ".txt", ios::binary);

    const size_t LIMIT = 1024 * 1024; // 1 MB
    size_t textSize = 0;

    char ch;
    while (input.read(&ch, 1))
    {
        unsigned char uch = static_cast<unsigned char>(ch);

        // Split into quotient and remainder (base-92)
        unsigned char q = uch / 92;
        unsigned char r = uch % 92;

        char c1 = charset[q];
        char c2 = charset[r];

        // Write two characters
        output.write(&c1, 1);
        output.write(&c2, 1);

        textSize += 2;

        // Split file if exceeds limit
        if (textSize >= LIMIT)
        {
            output.close();
            output.open(to_string(++fileIndex) + ".txt", ios::binary);
            textSize = 0;
        }
    }

    input.close();
    output.close();

    cout << "Encoding complete. Files created: " << fileIndex << endl;
    return 0;
}
