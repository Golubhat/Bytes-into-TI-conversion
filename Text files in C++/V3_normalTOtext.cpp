#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main()
{
    string charset;
    for (int i = 35; i <= 126; i++) // 92 chars
        charset += char(i);

    string fileName;
    cout << "Enter input file name: ";
    getline(cin >> ws, fileName);

    ifstream input(fileName, ios::binary);
    if (!input)
    {
        cout << "Error opening input file\n";
        return 1;
    }

    int fileIndex = 1;
    ofstream output(to_string(fileIndex) + ".txt", ios::binary);

    const int LIMIT = 1024 * 1024;
    int textSize = 0;

    char ch;

    while (input.read(&ch, 1))
    {
        unsigned char uch = static_cast<unsigned char>(ch);

        unsigned char q = uch / 92;
        unsigned char r = uch % 92;

        if (q == 0)
        {
            // write only 1 char
            char c = charset[r];
            output.write(&c, 1);
            textSize += 1;
        }
        else
        {
            // write marker + char
            char marker = '!' + q - 1; // '!' → q=1, '"' → q=2
            char c = charset[r];

            output.write(&marker, 1);
            output.write(&c, 1);

            textSize += 2;
        }

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
}