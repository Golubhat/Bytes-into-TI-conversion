#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main()
{
    string charset;
    for (int i = 35; i <= 126; i++)
        charset += char(i);

    string outputFile;
    cout << "Enter output file name: ";
    getline(cin >> ws, outputFile);

    int numFiles;
    cout << "Enter number of text files: ";
    cin >> numFiles;

    ofstream output(outputFile, ios::binary);
    if (!output)
    {
        cout << "Error creating output file.\n";
        return 1;
    }

    for (int i = 1; i <= numFiles; i++)
    {
        ifstream input(to_string(i) + ".txt", ios::binary);
        if (!input)
        {
            cout << "Error opening file " << i << ".txt\n";
            return 1;
        }

        char c1, c2;

        while (input.read(&c1, 1) && input.read(&c2, 1))
        {
            int q = charset.find(c1);
            int r = charset.find(c2);

            if (q == string::npos || r == string::npos)
            {
                cout << "Invalid character in encoded file.\n";
                return 1;
            }

            unsigned char uch = q * 92 + r;
            char ch = static_cast<char>(uch);

            output.write(&ch, 1);
        }

        input.close();
    }

    output.close();

    cout << "Decoding complete.\n";
    return 0;
}
