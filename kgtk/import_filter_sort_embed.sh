kgtk import_ntriples -i $1 \
  --namespace-file prefixes.tsv | \
kgtk filter \
  -p " ; sd:name, sd:keyword, sd:description ; " | \
kgtk text-embedding \
	--save-embedding-sentence \
	--model bert-base-nli-cls-token \
	-f kgtk_format \
	--output-format kgtk_format \
	--property-value "sd:keyword" "sd:description"\
  --label-properties "sd:name" \
	--has-properties "" \
  --property-labels-file property_labels.tsv \
	> emb7.txt