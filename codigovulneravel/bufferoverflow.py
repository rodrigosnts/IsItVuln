Buffer Overflow

char buffer[contentLength];
int size = 0;
char ch;
static const int eof = std::char_traits<char>::eof();
while((ch = request.stream().get()) != eof) {
  buffer[size] = ch;
  size += 1;
}
std::istringstream requestBody(std::string(buffer, size));