tail -f ../../kodi.log | awk '
    error = /ERROR/ {print "\033[35m" $0 "\033[0m"}
    id = /\[script.service.brokensubs\]/ {print "\033[36m" $0 "\033[0m"}
    !error && !id {print $0}'
#tail -f ../../kodi.log
