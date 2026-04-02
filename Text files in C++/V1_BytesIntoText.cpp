#include <iostream>
#include <fstream>
#include <string>
using namespace std;

void encodeAndSplit()
{
    unsigned char ch;
    char code[2];
    fstream input, output;
    string fileName;

    cout << "Enter file name for input: ";
    getline(cin >> ws, fileName);

    input.open(fileName, ios::in | ios::binary);
    if (!input)
    {
        cout << "Error opening input file!\n";
        return;
    }

    input.seekg(0, ios::end);
    long long int i, totalSize = input.tellg();
    input.seekg(0, ios::beg);

    int textLimit = 0, num = 1;
    output.open("1.txt", ios::out | ios::binary);

    for (i = 1; i <= totalSize; i++)
    {
        if (textLimit++ < 1024 * 1024) // 1 MB
        {
            input.read((char *)&ch, sizeof(ch));
            code[0] = (ch / 26) + 97;
            code[1] = (ch % 26) + 97;
            output.write((char *)code, 2 * sizeof(char));
        }
        else if (i < totalSize)
        {
            output.close();
            textLimit = 0;
            output.open(to_string(++num) + ".txt", ios::out | ios::binary);
        }
    }

    cout << "Done! Files created: " << num << endl;

    output.close();
    input.close();
}

void decodeAndMerge()
{
    char code[2];
    unsigned char ch;
    fstream input, output;
    string fileName;

    cout << "Enter file name for output: ";
    getline(cin >> ws, fileName);

    int num;
    cout << "Enter number of text files: ";
    cin >> num;

    output.open(fileName, ios::out | ios::binary);
    if (!output)
    {
        cout << "Error opening output file!\n";
        return;
    }

    for (int i = 1; i <= num; i++)
    {
        input.open(to_string(i) + ".txt", ios::in | ios::binary);
        if (!input)
        {
            cout << "Error opening file: " << i << ".txt\n";
            continue;
        }

        input.seekg(0, ios::end);
        long long int limit = input.tellg();
        input.seekg(0, ios::beg);

        for (long long int j = 0; j < limit; j += 2)
        {
            input.read((char *)code, 2 * sizeof(char));
            ch = 26 * (code[0] - 97) + (code[1] - 97);
            output.write((char *)&ch, sizeof(ch));
        }

        input.close();
    }

    cout << "Done!";

    output.close();
}

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
