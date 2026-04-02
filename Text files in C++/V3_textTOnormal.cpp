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
        cout << "Error creating output file\n";
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

        char code;

        while (input.read(&code, 1))
        {
            unsigned char q = 0;
            char r_char;

            if (code < 35) // marker range ('!'=33, '"'=34)
            {
                q = (code - '!') + 1;

                if (!input.read(&r_char, 1))
                    break;
            }
            else
            {
                // single char case
                r_char = code;
                q = 0;
            }

            int r = charset.find(r_char);
            if (r == string::npos)
            {
                cout << "Invalid character found\n";
                return 1;
            }

            unsigned char uch = q * 92 + r;
            char original = static_cast<char>(uch);

            output.write(&original, 1);
        }

        input.close();
    }

    output.close();

    cout << "Decoding complete.\n";
}