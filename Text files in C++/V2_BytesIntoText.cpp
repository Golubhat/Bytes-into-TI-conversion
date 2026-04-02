#include <iostream>
#include <fstream>
#include <string>
using namespace std;

// Charset generator
string getCharset()
{
    string charset;
    for (int i = 35; i <= 126; i++) // 92 chars
        charset += char(i);
    return charset;
}

// Encode + Split (optimized)
void encodeAndSplit()
{
    string charset = getCharset();

    string fileName;
    cout << "Enter input file name: ";
    getline(cin >> ws, fileName);

    ifstream input(fileName, ios::binary);
    if (!input)
    {
        cout << "Error opening input file\n";
        return;
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
            // 1 character case
            char c = charset[r];
            output.write(&c, 1);
            textSize += 1;
        }
        else
        {
            // marker + character
            char marker = '!' + q - 1; // '!' => q=1
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

    cout << "Done! Files created: " << fileIndex << endl;
}

// Decode + Merge
void decodeAndMerge()
{
    string charset = getCharset();

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
        return;
    }

    for (int i = 1; i <= numFiles; i++)
    {
        ifstream input(to_string(i) + ".txt", ios::binary);
        if (!input)
        {
            cout << "Error opening file " << i << ".txt\n";
            return;
        }

        char code;

        while (input.read(&code, 1))
        {
            unsigned char q = 0;
            char r_char;

            if (code < 35) // marker ('!'=33, '"'=34)
            {
                q = (code - '!') + 1;

                if (!input.read(&r_char, 1))
                    break;
            }
            else
            {
                r_char = code;
                q = 0;
            }

            int r = charset.find(r_char);
            if (r == string::npos)
            {
                cout << "Invalid character found\n";
                return;
            }

            unsigned char uch = q * 92 + r;
            char original = static_cast<char>(uch);

            output.write(&original, 1);
        }

        input.close();
    }

    output.close();

    cout << "Done!";
}

// Main menu
int main()
{
    int choice;

    cout << "1. Normal file bytes into text files\n";
    cout << "2. Text files into normal file bytes\n";
    cout << "Enter your choice: ";
    cin >> choice;

    switch (choice)
    {
    case 1:
        encodeAndSplit();
        break;
    case 2:
        decodeAndMerge();
        break;
    default:
        cout << "Invalid choice!\n";
    }

    return 0;
}
