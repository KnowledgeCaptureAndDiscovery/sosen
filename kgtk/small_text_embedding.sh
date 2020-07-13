#!/bin/bash
cat small_graph.tsv | kgtk text-embedding --debug \
	--embedding-projector-metadata-path embeddings \
	--save-embedding-sentence \
	--model bert-base-nli-cls-token \
	-f kgtk_format \
	--output-format kgtk_format \
	--isa-properties "n4:type" \
  --property-value "n7:keyword" "n7:description"\
  --label-properties "n7:name" "n6:label" \
	--has-properties "all" \
  --property-labels-file property_labels.tsv \
	> emb6.txt


#--description-properties "n7:description" \