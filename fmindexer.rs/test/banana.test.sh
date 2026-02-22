fmindexer build <(echo 'BANANA') banana.fmi

# Case: "ANA" in "BANANA" (2 results)
fmindexer search banana.fmi 'ANA' >output
cat >expected <<EOF
1
3
EOF
diff output expected

# Case: "AB" in "BANANA" (no results)
fmindexer search banana.fmi 'AB' >output
printf '' >expected
diff output expected
