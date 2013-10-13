#!/usr/bin/perl

$DB=$ENV{DB};
$DBUSER=$ENV{DBUSER};
$DBPASS=$ENV{DBPASS};
$DBHOST=$ENV{DBHOST};
$BASE=$ENV{BASE};
$STYLE_ID=$ENV{STYLE_ID};

%error_keys = ();

# possible_values: return list of all possible values for a key
sub possible_values {
  my $key = $_[0];
# TODO: escape characters
  my @ret = ();

  my $v;
  my $r;
# TODO: user/pass/host parameters for psql
  open $v, "psql -d \"dbname=$DB user=$DBUSER host=$DBHOST password=$DBPASS\" -t -A -c \"select (CASE WHEN value is null THEN 'NULL' ELSE value END) from (select key, unnest(cast(value as text[])) as value from each((${STYLE_ID}_stat()).properties_values)) t where key='$key';\"|";
  while($r = <$v>) {
    chop($r);
    push @ret, $r;
  }

  return @ret;
}

sub process {
  my $f = $_[0];
  my @keys = @{$_[1]};
  my $rek = $_[2];
  my @t = ();
  my @res;

  while (<$f>) {
    if (m/^# FOR (.*)$/) {
      my @k = split " ", $1;

      push @t, process($f, \@k, $rek+1);
    }
    elsif (m/^# END/) {
      last;
    }
    else {
      push @t, $_;
    }
  }

  foreach $key (@keys) {
    @res = ();

    foreach $value (possible_values($key)) {
      if ($value eq 'NULL') {
      }
      elsif ($value eq '*') {
	$error_keys{$key} = 1;
      }
      else {
	foreach $row (@t) {
	  my $r1 = $row;
	  $r1 =~ s/\[$key\]/$value/;
	  push @res, $r1;
	}
      }
    }

    @t = @res;
  }

  return @t;
}

# now process test-template.mapnik and replace COLOR placeholders by colors
open $f, "<${BASE}-template.mapnik";
open $r, ">${STYLE_ID}.mapnik";

@t = process($f, \(), 0);
$t = join "", @t;
$t =~ s/DBUSER/$DBUSER/ge;
$t =~ s/DBPASS/$DBPASS/ge;
$t =~ s/DBHOST/$DBHOST/ge;
$t =~ s/DB/${DB}/ge;
$t =~ s/STYLE_ID/$STYLE_ID/ge;

# replace canvas tags
open $v, "psql -d \"dbname=$DB user=$DBUSER host=$DBHOST password=$DBPASS\" -t -F '\t' -A -c \"select (each(properties)).key, (each(properties)).value from ${STYLE_ID}_check(pgmapcss_object('', '', null, Array['canvas']), pgmapcss_render_context(null, null));;\"|";
while($r1 = <$v>) {
  chop($r1);
  @r1 = split("\t", $r1);
  $t =~ s/\[canvas.$r1[0]\]/$r1[1]/ge;
}

print $r $t;

close($r);
close($f);

@error_keys = keys %error_keys;
if (@error_keys != 0) {
  print "WARNING! Some values for the following keys are calculated by an eval-statement. As pgmapcss can't guess the result of those statements some symbols might not get rendered.\n* ";
  print join("\n* ", @error_keys);
  print "\n";
}
