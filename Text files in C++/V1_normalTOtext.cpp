#include <iostream>
#include <fstream>
using namespace std;
int main()
{
    unsigned char ch;
    char code[2];
    fstream input, output;
    string fileName;
    cout << "Enter file name for input: ";
    getline(cin >> ws, fileName);
    input.open(fileName, ios::in | ios::binary);
    input.seekg(0, ios::end);
    long long int i, totalSize = input.tellg();
    input.seekg(0, ios::beg);

    int textLimit = 0, num = 1;
    output.open("1.txt", ios::out | ios::binary);
    for (i = 1; i <= totalSize; i++)
    {
        if (textLimit++ < 536870911) // 536870911*2 is the Maximum Readable Limit by Notepad
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
    output.close();
    input.close();
}
