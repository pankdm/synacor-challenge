#include <stdio.h>
#include <iostream>
#include <vector>
#include <string>
#include <math.h>
#include <algorithm>
#include <bitset>
#include <set>
#include <sstream>
#include <stdlib.h>
#include <map>
#include <queue>
#include <assert.h>
#include <deque>
#include <string.h>


using namespace std;

#define sz(x) ((int)x.size())
#define all(x) (x).begin(), (x).end()
#define pb(x) push_back(x)
#define mp(x, y) make_pair(x, y)

typedef long long int64;

typedef vector <int64> vi;
typedef vector <vi> vvi;

    // if a == 2:
    //     return mod(2 * c + 1 + (c + 1) * b), False
  // for i in xrange(start, end):
  //     dp[i] = mod( dp[i - 1] * (c + 1) + 1 + 2 * c )

const int64 MX = 32768;
const int64 MOD = 32768;

int64 mod(int64 v) {
  return ((v % MOD) + MOD) % MOD;
}

int64 f2(int64 c) {
  return mod(2 * c + 1 + (c + 1) * c);
}

void solution() {
  for (int c = 1; c < MX; ++c) {
    vi dp(MX, 0);
    dp[0] = f2(c);
    for (int i = 1; i < MX; ++i) {
      dp[i] = mod( dp[i - 1] * (c + 1) + 1 + 2 * c );
    }
    int64 value = dp[ dp[c] ];
    cout << "dp[ " << c << " ] = " << value << endl;
    if (value == 6) {
      cout << "Found ans: " << value << endl;
      return;
    }
  }
}

int main () {
	//freopen("", "rt", stdin);
	//freopen("", "wt", stdout);
	//std::ios::sync_with_stdio(false);
  solution();
  return 0;
}
